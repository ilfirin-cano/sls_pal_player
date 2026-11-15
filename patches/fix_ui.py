from pathlib import Path
p = Path("app/src/main/java/dev/soulseek/player/MainActivity.kt")
s = p.read_text()
s = s.replace("import androidx.compose.foundation.layout.*\n", "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.rememberScrollState\nimport androidx.compose.foundation.verticalScroll\n")
s = s.replace("import androidx.compose.runtime.*\n", "import androidx.compose.runtime.*\nimport androidx.compose.ui.platform.LocalContext\nimport androidx.compose.runtime.saveable.rememberSaveable\nimport kotlinx.coroutines.launch\nimport dev.soulseek.player.data.local.ConnectionStore\nimport dev.soulseek.player.data.navidrome.NavidromeCredentials\nimport androidx.compose.ui.text.input.PasswordVisualTransformation\n")
s = s.replace("Column(Modifier.fillMaxSize().padding(padding).padding(horizontal = 20.dp)) {", "Column(Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {")
start = s.index("@Composable\nprivate fun SettingsScreen()")
end = s.index("@Composable\nprivate fun MiniPlayer", start)
settings = r'''@Composable
private fun SettingsScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val store = remember(context) { ConnectionStore(context) }
    val prefs = remember(context) { context.getSharedPreferences("player_ui_settings", android.content.Context.MODE_PRIVATE) }
    var dialog by rememberSaveable { mutableStateOf("") }
    var serverUrl by rememberSaveable { mutableStateOf(prefs.getString("server_url", "") ?: "") }
    var username by rememberSaveable { mutableStateOf(prefs.getString("server_user", "") ?: "") }
    var password by rememberSaveable { mutableStateOf("") }
    var queueUrl by rememberSaveable { mutableStateOf(prefs.getString("queue_url", "") ?: "") }
    var quality by rememberSaveable { mutableStateOf(prefs.getString("quality", "Автоматически") ?: "Автоматически") }
    var scrobbling by rememberSaveable { mutableStateOf(prefs.getString("scrobbling", "Navidrome") ?: "Navidrome") }
    var theme by rememberSaveable { mutableStateOf(prefs.getString("theme", "Системная") ?: "Системная") }
    var status by remember { mutableStateOf("") }
    SectionTitle("Подключения")
    SettingRow("Navidrome", serverUrl.ifBlank { "Адрес сервера, логин и пароль" }) { dialog = "navidrome" }
    SettingRow("soulseek-queue", queueUrl.ifBlank { "URL рекомендательного API" }) { dialog = "queue" }
    SectionTitle("Воспроизведение")
    SettingRow("Качество потока", quality) { dialog = "quality" }
    SettingRow("Scrobbling", scrobbling) { dialog = "scrobbling" }
    SettingRow("Тема", theme) { dialog = "theme" }
    if (status.isNotBlank()) Text(status, color = Accent, fontSize = 12.sp, modifier = Modifier.padding(top = 10.dp))
    Text("Учетные данные Navidrome хранятся в зашифрованном хранилище Android.", color = MaterialTheme.colorScheme.onSurface.copy(alpha=.62f), fontSize = 12.sp, modifier = Modifier.padding(top = 16.dp, bottom = 24.dp))
    when (dialog) {
        "navidrome" -> AlertDialog(onDismissRequest = { dialog = "" }, title = { Text("Подключение Navidrome") },
            text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(serverUrl, { serverUrl = it }, label = { Text("URL сервера") }, placeholder = { Text("https://music.example.com") }, singleLine = true)
                OutlinedTextField(username, { username = it }, label = { Text("Логин") }, singleLine = true)
                OutlinedTextField(password, { password = it }, label = { Text("Пароль") }, visualTransformation = PasswordVisualTransformation(), singleLine = true)
            } },
            confirmButton = { TextButton(onClick = { scope.launch { try {
                require(serverUrl.startsWith("https://") || serverUrl.startsWith("http://")) { "Укажите URL с http:// или https://" }
                store.save(NavidromeCredentials(serverUrl, username, password, null))
                prefs.edit().putString("server_url", serverUrl.trim().trimEnd('/')).putString("server_user", username).apply()
                password = ""; status = "Настройки Navidrome сохранены"; dialog = ""
            } catch (e: Exception) { status = e.message ?: "Не удалось сохранить настройки" } } }) { Text("Сохранить") } },
            dismissButton = { TextButton(onClick = { dialog = "" }) { Text("Отмена") } })
        "queue" -> AlertDialog(onDismissRequest = { dialog = "" }, title = { Text("soulseek-queue") },
            text = { OutlinedTextField(queueUrl, { queueUrl = it }, label = { Text("URL API") }, placeholder = { Text("https://queue.example.com") }, singleLine = true) },
            confirmButton = { TextButton(onClick = { prefs.edit().putString("queue_url", queueUrl.trim().trimEnd('/')).apply(); status = "URL soulseek-queue сохранён"; dialog = "" }) { Text("Сохранить") } },
            dismissButton = { TextButton(onClick = { dialog = "" }) { Text("Отмена") } })
        "quality", "scrobbling", "theme" -> {
            val title = when (dialog) { "quality" -> "Качество потока"; "scrobbling" -> "Scrobbling"; else -> "Тема" }
            val options = when (dialog) { "quality" -> listOf("Автоматически", "Высокое", "Среднее", "Экономия трафика"); "scrobbling" -> listOf("Navidrome", "Last.fm", "Выключено"); else -> listOf("Системная", "Тёмная", "Светлая") }
            val selected = when (dialog) { "quality" -> quality; "scrobbling" -> scrobbling; else -> theme }
            AlertDialog(onDismissRequest = { dialog = "" }, title = { Text(title) },
                text = { Column { options.forEach { option -> Row(Modifier.fillMaxWidth().clickable {
                    when (dialog) { "quality" -> { quality = option; prefs.edit().putString("quality", option).apply() }; "scrobbling" -> { scrobbling = option; prefs.edit().putString("scrobbling", option).apply() }; else -> { theme = option; prefs.edit().putString("theme", option).apply() } }; dialog = ""
                }.padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(selected == option, onClick = { when (dialog) { "quality" -> { quality = option; prefs.edit().putString("quality", option).apply() }; "scrobbling" -> { scrobbling = option; prefs.edit().putString("scrobbling", option).apply() }; else -> { theme = option; prefs.edit().putString("theme", option).apply() } }; dialog = "" })
                    Spacer(Modifier.width(8.dp)); Text(option)
                } } } }, confirmButton = { TextButton(onClick = { dialog = "" }) { Text("Закрыть") } })
        }
    }
}
@Composable
private fun SettingRow(title: String, subtitle: String, onClick: () -> Unit) {
    Card(Modifier.fillMaxWidth().padding(bottom = 8.dp).clickable(onClick = onClick), colors = CardDefaults.cardColors(containerColor = Surface), shape = RoundedCornerShape(16.dp)) {
        Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) { Text(title, fontWeight = FontWeight.SemiBold); Text(subtitle, color = MaterialTheme.colorScheme.onSurface.copy(alpha=.62f), fontSize = 12.sp) }
            Icon(Icons.Default.Settings, contentDescription = "Изменить", tint = Accent, modifier = Modifier.size(18.dp))
        }
    }
}

'''
s = s[:start] + settings + s[end:]
p.write_text(s)
