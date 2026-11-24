pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    // Integración con GitHub: Jenkins consulta el repositorio cada ~2 minutos (Poll SCM)
    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        COMPOSE_PROJECT_NAME = 'jenkins-proyecto'
        POSTGRES_DB          = 'proyecto'
        POSTGRES_USER        = 'usuario'
        // La contraseña viene de las credenciales de Jenkins (Secret text, id: db-password).
        // Nunca se escribe en el código ni en el repositorio.
        POSTGRES_PASSWORD    = credentials('db-password')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build') {
            steps {
                // Construye la imagen de app (contenedor 1); db usa postgres:16.4 (contenedor 2)
                sh 'docker compose build'
                sh 'docker compose config --images'
            }
        }

        stage('Test') {
            steps {
                sh 'docker compose up -d'
                // La prueba corre DENTRO del contenedor app: guarda y lee una nota,
                // y exige que la app use el host "db" (nombre del servicio).
                // Si algo falla, sale con código distinto de 0 y el build falla.
                sh 'docker compose exec -T app python - < tests/test_comunicacion.py'
                sh 'docker compose ps'
            }
        }
    }

    post {
        always {
            sh 'docker compose logs --no-color --tail=40 || true'
            sh 'docker compose down -v || true'
        }
        success {
            echo 'BUILD EXITOSO: los dos contenedores se construyeron y se comunican por el nombre del servicio.'
        }
        failure {
            echo 'BUILD FALLIDO: revisa la salida de consola de la etapa que quedó en rojo.'
        }
    }
}
