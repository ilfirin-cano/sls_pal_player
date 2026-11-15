from pathlib import Path
p = Path("app/src/main/java/dev/soulseek/player/MainActivity.kt")
s = p.read_text()
s = s.replace("import dev.soulseek.player.data.navidrome.NavidromeCredentials\n", """import dev.soulseek.player.data.navidrome.NavidromeCredentials
import dev.soulseek.player.data.navidrome.NavidromeHttpClient
import dev.soulseek.player.data.navidrome.NavidromeRepository
import dev.soulseek.player.data.navidrome.SubsonicResult
import dev.soulseek.player.data.recommendations.RecommendationHttpClient
import dev.soulseek.player.data.local.DatabaseProvider
import dev.soulseek.player.data.local.CachedSongEntity
import kotlinx.coroutines.flow.first
""")
s=s.replace('private fun LibraryScreen(title: String = "Библиотека") {\n    Column {', '''private fun LibraryScreen(title: String = "Библиотека") {
    val context = LocalContext.current
    val songs by DatabaseProvider.get(context).playerDao().cachedSongs().collectAsState(initial = emptyList())
    Column {''')
s=s.replace('''        SectionTitle(title)
        EmptyState("Библиотека пока пуста", "Подключитесь к серверу Navidrome в настройках.")
    }
}''','''        SectionTitle(title, if (songs.isEmpty()) "Нет треков" else "${songs.size} треков")
        if (songs.isEmpty()) EmptyState("Библиотека пока пуста", "Настройте Navidrome и нажмите «Обновить библиотеку» в настройках.")
        else songs.forEach { song ->
            Row(Modifier.fillMaxWidth().padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Album, null, tint = Accent)
                Column(Modifier.weight(1f).padding(start = 12.dp)) {
                    Text(song.title, fontWeight = FontWeight.Medium)
                    Text(listOfNotNull(song.artist, song.album).joinToString(" • "), color = MaterialTheme.colorScheme.onSurface.copy(alpha=.62f), fontSize = 12.sp)
                }
            }
        }
    }
}''')
s=s.replace('private fun SettingsScreen() {','private fun SettingsScreen() {')
# Add loading of saved secure credentials after local state declarations
s=s.replace('''    var status by remember { mutableStateOf("") }
    SectionTitle("Подключения")''','''    var status by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        store.server.first()?.let { saved ->
            serverUrl = saved.baseUrl
            username = saved.username
        }
    }
    SectionTitle("Подключения")''')
s=s.replace('''    SettingRow("soulseek-queue", queueUrl.ifBlank { "URL рекомендательного API" }) { dialog = "queue" }
    SectionTitle("Воспроизведение")''','''    SettingRow("soulseek-queue", queueUrl.ifBlank { "URL рекомендательного API" }) { dialog = "queue" }
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedButton(enabled = !busy, modifier = Modifier.weight(1f), onClick = {
            scope.launch {
                busy = true; status = "Проверка Navidrome…"
                try {
                    val credentials = store.server.first() ?: error("Сначала сохраните адрес, логин и пароль Navidrome")
                    val repository = NavidromeRepository(NavidromeHttpClient().create(credentials.baseUrl), { credentials })
                    when (val result = repository.connect()) {
                        is SubsonicResult.Success -> status = "Navidrome подключён · версия ${result.value.serverVersion}"
                        is SubsonicResult.Failure -> status = "Ошибка Navidrome: ${result.reason}"
                    }
                } catch (e: Exception) { status = "Ошибка Navidrome: ${e.message ?: "не удалось подключиться"}" }
                finally { busy = false }
            }
        }) { Text("Проверить Navidrome", fontSize = 11.sp) }
        OutlinedButton(enabled = !busy, modifier = Modifier.weight(1f), onClick = {
            scope.launch {
                busy = true; status = "Проверка soulseek-queue…"
                try {
                    val url = queueUrl.trim().trimEnd('/')
                    require(url.startsWith("https://") || url.startsWith("http://")) { "Сначала укажите URL soulseek-queue" }
                    val health = RecommendationHttpClient().create(url).queueHealth()
                    status = "soulseek-queue доступен · состояние: ${health.state}"
                } catch (e: Exception) { status = "Ошибка soulseek-queue: ${e.message ?: "не удалось подключиться"}" }
                finally { busy = false }
            }
        }) { Text("Проверить queue", fontSize = 11.sp) }
    }
    Button(enabled = !busy, modifier = Modifier.fillMaxWidth().padding(top = 8.dp), onClick = {
        scope.launch {
            busy = true; status = "Загрузка библиотеки Navidrome…"
            try {
                val credentials = store.server.first() ?: error("Сначала сохраните подключение Navidrome")
                val repository = NavidromeRepository(NavidromeHttpClient().create(credentials.baseUrl), { credentials })
                when (val connection = repository.connect()) {
                    is SubsonicResult.Failure -> error(connection.reason)
                    is SubsonicResult.Success -> Unit
                }
                val dao = DatabaseProvider.get(context).playerDao()
                val cached = mutableListOf<CachedSongEntity>()
                var offset = 0
                while (true) {
                    val page = when (val result = repository.albums(size = 100, offset = offset)) {
                        is SubsonicResult.Success -> result.value
                        is SubsonicResult.Failure -> error(result.reason)
                    }
                    if (page.isEmpty()) break
                    page.forEach { albumSummary ->
                        val album = when (val result = repository.album(albumSummary.id)) {
                            is SubsonicResult.Success -> result.value
                            is SubsonicResult.Failure -> null
                        }
                        album?.song.orEmpty().forEach { song ->
                            cached.add(CachedSongEntity(song.id, song.title, song.artist ?: album?.artist, song.album ?: album?.name, song.albumId ?: album?.id, song.artistId ?: album?.artistId, song.coverArt ?: album?.coverArt, song.duration?.toLong(), System.currentTimeMillis()))
                        }
                    }
                    offset += page.size
                    if (page.size < 100) break
                }
                if (cached.isNotEmpty()) dao.cacheSongs(cached)
                status = "Библиотека обновлена: ${cached.size} треков из Navidrome"
            } catch (e: Exception) { status = "Ошибка обновления библиотеки: ${e.message ?: "не удалось загрузить данные"}" }
            finally { busy = false }
        }
    }) { Text(if (busy) "Подождите…" else "Обновить библиотеку") }
    SectionTitle("Воспроизведение")''')
# Save with blank password should retain existing stored password
s=s.replace('''                store.save(NavidromeCredentials(serverUrl, username, password, null))
                prefs.edit()''','''                val existingPassword = store.server.first()?.password.orEmpty()
                val passwordToSave = password.ifBlank { existingPassword }
                require(passwordToSave.isNotBlank()) { "Введите пароль Navidrome" }
                store.save(NavidromeCredentials(serverUrl, username, passwordToSave, null))
                prefs.edit()''')
# queue dialog persist normalized and refresh field text via same state already
p.write_text(s)

# Allow user-configured HTTP endpoints for self-hosted LAN servers. HTTPS remains recommended.
manifest = Path("app/src/main/AndroidManifest.xml")
m = manifest.read_text().replace('android:usesCleartextTraffic="false"', 'android:usesCleartextTraffic="true"')
manifest.write_text(m)
