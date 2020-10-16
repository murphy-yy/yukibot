plugins {
    kotlin("jvm") version "1.4.10"
    id("com.github.johnrengelman.shadow") version "6.1.0"
}

group = "io.github.yukileafx"
version = "4.0"

repositories {
    mavenCentral()
    jcenter()
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("net.dv8tion:JDA:4.2.0_209")
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

    build {
        dependsOn("clean", "shadowJar")
        mustRunAfter("clean")
    }
}
