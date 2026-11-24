# Jenkins (Entrega 2)

Jenkins corre en un contenedor (`jenkins/jenkins:lts-jdk21` + Docker CLI) con el volumen `jenkins_home`.

```bash
cd jenkins
docker compose up -d --build
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

- Interfaz web: puerto 8080.
- Credenciales guardadas en Jenkins: `github-credentials` (usuario + token) y `db-password` (Secret text).
- El pipeline está en el `Jenkinsfile` de la raíz del repositorio; la prueba, en `tests/test_comunicacion.py`.
