package com.recoverx.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import com.recoverx.app.RecoverXApplication
import com.recoverx.navigation.RecoverXNavGraph
import com.recoverx.ui.theme.RecoverXTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val app = application as RecoverXApplication
        val container = app.container

        setContent {
            RecoverXTheme {
                val navController = rememberNavController()
                RecoverXNavGraph(
                    navController = navController,
                    container = container
                )
            }
        }
    }
}
