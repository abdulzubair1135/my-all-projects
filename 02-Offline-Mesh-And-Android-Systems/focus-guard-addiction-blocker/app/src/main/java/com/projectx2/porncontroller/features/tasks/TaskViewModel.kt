package com.projectx2.porncontroller.features.tasks

import android.app.Application
import android.content.Context
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.database.entities.TaskHistory
import com.projectx2.porncontroller.core.database.entities.TaskItem
import com.projectx2.porncontroller.services.TaskTimerService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class TaskUiState(
    val tasks: List<TaskItem> = emptyList(),
    val taskHistory: List<TaskHistory> = emptyList(),
    val selectedCategory: String = "ALL",
    val activeTaskId: Long? = null,
    val remainingSeconds: Int = 0,
    val isPaused: Boolean = false
)

private data class TimerState(
    val activeTaskId: Long?,
    val remainingSeconds: Int,
    val isPaused: Boolean
)

class TaskViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PornControllerApp).repository
    private val context: Context = application.applicationContext

    private val _selectedCategory = MutableStateFlow("ALL")
    private val _uiState = MutableStateFlow(TaskUiState())
    val uiState: StateFlow<TaskUiState> = _uiState.asStateFlow()

    init {
        val timerStateFlow: Flow<TimerState> = combine(
            TaskTimerService.activeTaskIdFlow,
            TaskTimerService.remainingSecondsFlow,
            TaskTimerService.isPausedFlow
        ) { activeId, remaining, isPaused ->
            TimerState(activeId, remaining, isPaused)
        }

        viewModelScope.launch {
            combine(
                repo.activeTasksFlow,
                repo.taskHistoryFlow,
                _selectedCategory,
                timerStateFlow
            ) { tasks, history, category, timerState ->
                val filtered = if (category == "ALL") tasks else tasks.filter { it.category == category }
                TaskUiState(
                    tasks = filtered,
                    taskHistory = history,
                    selectedCategory = category,
                    activeTaskId = timerState.activeTaskId,
                    remainingSeconds = timerState.remainingSeconds,
                    isPaused = timerState.isPaused
                )
            }.collect {
                _uiState.value = it
            }
        }
    }

    fun selectCategory(cat: String) {
        _selectedCategory.value = cat
    }

    fun addTask(title: String, description: String, durationMinutes: Int, category: String, isPhysical: Boolean) {
        viewModelScope.launch {
            repo.insertTask(
                TaskItem(
                    title = title,
                    description = description,
                    durationSeconds = durationMinutes * 60,
                    category = category,
                    isPhysical = isPhysical
                )
            )
        }
    }

    fun deleteTask(item: TaskItem) {
        viewModelScope.launch {
            repo.deleteTask(item)
        }
    }

    fun startTaskTimer(task: TaskItem) {
        val intent = Intent(context, TaskTimerService::class.java).apply {
            action = TaskTimerService.ACTION_START
            putExtra(TaskTimerService.EXTRA_TASK_ID, task.id)
            putExtra(TaskTimerService.EXTRA_TASK_TITLE, task.title)
            putExtra(TaskTimerService.EXTRA_DURATION_SECONDS, task.durationSeconds)
        }
        context.startService(intent)
    }

    fun pauseTimer() {
        val intent = Intent(context, TaskTimerService::class.java).apply {
            action = TaskTimerService.ACTION_PAUSE
        }
        context.startService(intent)
    }

    fun resumeTimer() {
        val intent = Intent(context, TaskTimerService::class.java).apply {
            action = TaskTimerService.ACTION_RESUME
        }
        context.startService(intent)
    }

    fun completeTimer() {
        val intent = Intent(context, TaskTimerService::class.java).apply {
            action = TaskTimerService.ACTION_COMPLETE
        }
        context.startService(intent)
    }

    fun cancelTimer() {
        val intent = Intent(context, TaskTimerService::class.java).apply {
            action = TaskTimerService.ACTION_CANCEL
        }
        context.startService(intent)
    }
}
