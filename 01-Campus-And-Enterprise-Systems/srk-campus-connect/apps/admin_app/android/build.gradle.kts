allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir = file("C:/temp/flutter_build/admin_app")
rootProject.layout.buildDirectory.set(newBuildDir)

subprojects {
    val newSubprojectBuildDir = file("C:/temp/flutter_build/admin_app/${project.name}")
    project.layout.buildDirectory.set(newSubprojectBuildDir)
}

subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
