package life.pawhub.notes

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.room.*
import androidx.room.Room
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

@Entity(tableName = "notes")
data class Note(@PrimaryKey(autoGenerate = true) val id: Long = 0, val title: String = "", val body: String = "", val pinned: Boolean = false, val updatedAt: Long = System.currentTimeMillis())

@Dao interface NoteDao {
    @Query("SELECT * FROM notes ORDER BY pinned DESC, updatedAt DESC")
    fun observe(): Flow<List<Note>>
    @Insert(onConflict = OnConflictStrategy.REPLACE) suspend fun save(note: Note): Long
    @Delete suspend fun delete(note: Note)
}
@Database(entities = [Note::class], version = 1, exportSchema = false)
abstract class NotesDb : RoomDatabase() { abstract fun notes(): NoteDao }

class NotesVm(private val dao: NoteDao) : ViewModel() {
    val notes = dao.observe()
    fun save(note: Note) = viewModelScope.launch { dao.save(note.copy(updatedAt = System.currentTimeMillis())) }
    fun delete(note: Note) = viewModelScope.launch { dao.delete(note) }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val db = Room.databaseBuilder(applicationContext, NotesDb::class.java, "paw-notes.db").build()
        setContent {
            val vm: NotesVm = viewModel(factory = object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T = NotesVm(db.notes()) as T
            })
            PawApp(vm)
        }
    }
}

@Composable fun PawApp(vm: NotesVm) {
    val notes by vm.notes.collectAsState(initial = emptyList())
    var selected by remember { mutableStateOf<Note?>(null) }
    var editing by remember { mutableStateOf(false) }
    var query by remember { mutableStateOf("") }
    MaterialTheme(colorScheme = darkColorScheme()) {
        Surface(Modifier.fillMaxSize()) {
            if (editing) {
                val original = selected ?: Note()
                var title by remember(original.id, editing) { mutableStateOf(original.title) }
                var body by remember(original.id, editing) { mutableStateOf(original.body) }
                var pinned by remember(original.id, editing) { mutableStateOf(original.pinned) }
                fun finish() {
                    if (title.isNotBlank() || body.isNotBlank()) vm.save(original.copy(title = title, body = body, pinned = pinned))
                    editing = false
                }
                BackHandler { finish() }
                Column(Modifier.padding(20.dp)) {
                    TextButton(onClick = { finish() }) { Text("← Save & back") }
                    OutlinedTextField(title, { title = it }, label = { Text("Title") }, modifier = Modifier.fillMaxWidth())
                    Spacer(Modifier.height(12.dp))
                    OutlinedTextField(body, { body = it }, label = { Text("Note") }, modifier = Modifier.fillMaxWidth().weight(1f), minLines = 8)
                    Row {
                        TextButton(onClick = { pinned = !pinned }) { Text(if (pinned) "★ Pinned" else "☆ Pin") }
                        Spacer(Modifier.weight(1f))
                        if (original.id != 0L) TextButton(onClick = { vm.delete(original); editing = false }) { Text("Delete") }
                        Button(onClick = { finish() }) { Text("Save") }
                    }
                }
            } else {
                Column(Modifier.padding(20.dp)) {
                    Text("PawNote", style = MaterialTheme.typography.headlineLarge)
                    Text("Simply a note app.", style = MaterialTheme.typography.bodyMedium)
                    Spacer(Modifier.height(16.dp))
                    OutlinedTextField(query, { query = it }, label = { Text("Search notes") }, modifier = Modifier.fillMaxWidth())
                    Spacer(Modifier.height(12.dp))
                    Box(Modifier.weight(1f)) {
                        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            items(notes.filter { it.title.contains(query, true) || it.body.contains(query, true) }, key = { it.id }) { note ->
                                Card(Modifier.fillMaxWidth().clickable { selected = note; editing = true }, shape = RoundedCornerShape(16.dp)) {
                                    Column(Modifier.padding(16.dp)) {
                                        Text((if (note.pinned) "★ " else "") + (note.title.ifBlank { "Untitled" }), style = MaterialTheme.typography.titleMedium)
                                        Text(note.body, maxLines = 3)
                                    }
                                }
                            }
                        }
                    }
                    Button(onClick = { selected = Note(); editing = true }, modifier = Modifier.fillMaxWidth()) { Text("+ New note") }
                }
            }
        }
    }
}
