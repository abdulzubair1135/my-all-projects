package com.recoverx.recovery

import java.io.File

object CollisionResolver {

    fun resolveUniqueName(existingNames: Set<String>, baseName: String): String {
        if (!existingNames.contains(baseName)) {
            return baseName
        }

        val dot = baseName.lastIndexOf('.')
        val nameWithoutExt = if (dot > 0) baseName.substring(0, dot) else baseName
        val ext = if (dot > 0) baseName.substring(dot) else ""

        var counter = 1
        while (true) {
            val candidate = "$nameWithoutExt ($counter)$ext"
            if (!existingNames.contains(candidate)) {
                return candidate
            }
            counter++
        }
    }

    fun resolveUniqueFile(parentDir: File, desiredName: String): File {
        var file = File(parentDir, desiredName)
        if (!file.exists()) return file

        val dot = desiredName.lastIndexOf('.')
        val nameWithoutExt = if (dot > 0) desiredName.substring(0, dot) else desiredName
        val ext = if (dot > 0) desiredName.substring(dot) else ""

        var counter = 1
        while (file.exists()) {
            file = File(parentDir, "$nameWithoutExt ($counter)$ext")
            counter++
        }
        return file
    }
}
