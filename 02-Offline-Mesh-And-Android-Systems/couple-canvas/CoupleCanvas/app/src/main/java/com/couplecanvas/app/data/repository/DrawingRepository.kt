package com.couplecanvas.app.data.repository

import android.content.Context
import android.graphics.Bitmap
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.couplecanvas.app.data.local.DrawingDao
import com.couplecanvas.app.data.local.DrawingEntity
import com.couplecanvas.app.domain.model.CanvasOperation
import com.couplecanvas.app.domain.model.Drawing
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class DrawingRepository(
    private val context: Context,
    private val drawingDao: DrawingDao,
    private val gson: Gson = Gson()
) {

    val allDrawings: Flow<List<Drawing>> = drawingDao.getAllDrawings().map { entities ->
        entities.map { entityToDrawing(it) }
    }

    suspend fun getDrawingById(id: String): Drawing? = withContext(Dispatchers.IO) {
        val entity = drawingDao.getDrawingById(id)
        entity?.let { entityToDrawing(it) }
    }

    suspend fun saveDrawing(drawing: Drawing) = withContext(Dispatchers.IO) {
        val operationsJson = gson.toJson(drawing.operations)
        val entity = DrawingEntity(
            id = drawing.id,
            title = drawing.title,
            createdAt = drawing.createdAt,
            updatedAt = System.currentTimeMillis(),
            partnerName = drawing.partnerName,
            previewImagePath = drawing.previewImagePath,
            operationsJson = operationsJson
        )
        drawingDao.insertOrUpdateDrawing(entity)
    }

    suspend fun deleteDrawing(id: String) = withContext(Dispatchers.IO) {
        drawingDao.deleteDrawingById(id)
    }

    suspend fun deleteAllDrawings() = withContext(Dispatchers.IO) {
        drawingDao.deleteAllDrawings()
    }

    suspend fun exportBitmapToDisk(bitmap: Bitmap, title: String): String = withContext(Dispatchers.IO) {
        val exportsDir = File(context.filesDir, "exports")
        if (!exportsDir.exists()) {
            exportsDir.mkdirs()
        }
        val fileName = "CoupleCanvas_${title.replace("\\s+".toRegex(), "_")}_${System.currentTimeMillis()}.png"
        val file = File(exportsDir, fileName)

        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
        file.absolutePath
    }

    private fun entityToDrawing(entity: DrawingEntity): Drawing {
        val type = object : TypeToken<List<CanvasOperation>>() {}.type
        val operations: List<CanvasOperation> = try {
            gson.fromJson(entity.operationsJson, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
        return Drawing(
            id = entity.id,
            title = entity.title,
            createdAt = entity.createdAt,
            updatedAt = entity.updatedAt,
            partnerName = entity.partnerName,
            previewImagePath = entity.previewImagePath,
            operations = operations
        )
    }
}
