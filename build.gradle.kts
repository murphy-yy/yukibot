plugins {
    kotlin("jvm") version "1.4.10"
    id("com.github.johnrengelman.shadow") version "6.1.0"
}

group = "io.github.yukileafx"
version = "4.1"

repositories {
    mavenCentral()
    jcenter()
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("net.dv8tion:JDA:4.2.0_209")
    implementation("com.jagrosh:jda-utilities:3.0.4")
    implementation("com.vdurmont:emoji-java:5.1.1")
    implementation("com.sedmelluq:lavaplayer:1.3.50")
}

tasks {
    compileKotlin {
        kotlinOptions.jvmTarget = "1.8"
    }

    compileTestKotlin {
        kotlinOptions.jvmTarget = "1.8"
    }

    jar {
        manifest {
            attributes["Main-Class"] = "io.github.yukileafx.yukibot.YukiBotKt"
        }
    }

    shadowJar {
        archiveVersion.set("")
    }

    task("stage") {
        dependsOn("clean", "shadowJar")
    }
}
