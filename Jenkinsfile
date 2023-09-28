pipeline {
    agent any

    environment {
        IMAGE_NAME = "remind_bot"
        REMOTE_NAME = "PipelineRemoteServer"
        REMOTE_HOST =  "chiptune.iptime.org"
        REMOTE_CREDENTIAL_ID = "chiptune"
        SOURCE_FILES = "Cogs/**/*, reminerbot.py, dockerfile, docker-compose.yml, requirement.txt"
        REMOTE_DIRECTORY = "/service/remind_bot"
    }

    stages {

        // 프로젝트 빌드 및 테스트
        stage("CI: Project Build") {
            steps {
                sh 'echo python build skiped. it will be build in docker.'
            }
        }

        // 배포 대상 서버에 dockerfile, docker-compose 파일, JAR 파일 전달
        stage("CI: Transfer Files") {
            steps {
                script {
                    // SSH 플러그인을 사용하여 명령 실행
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: "${REMOTE_NAME}",
                                verbose: true,
                                transfers: [
                                    sshTransfer(
                                        execCommand: '', // 원격 명령 (비워둘 수 있음)
                                        execTimeout: 120000, // 명령 실행 제한 시간 (밀리초)
                                        flatten: false, // true로 설정하면 원격 경로에서 파일이 복사됩니다.
                                        makeEmptyDirs: false, // true로 설정하면 원격 디렉토리에 빈 디렉토리가 생성됩니다.
                                        noDefaultExcludes: false,
                                        patternSeparator: '[, ]+',
                                        remoteDirectory: "${REMOTE_DIRECTORY}",
                                        remoteDirectorySDF: false,
                                        removePrefix: '', // 원본 파일 경로에서 제거할 접두사
                                        sourceFiles: "${SOURCE_FILES}"
                                    )
                                ]
                            )
                        ]
                    )
                }
            }
        }

        // docker image build
        stage("CI: Docker Build") {
            steps {
                script {
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: "${REMOTE_NAME}",
                                verbose: true,
                                transfers: [
                                    sshTransfer(
                                        execCommand: """cd ~${REMOTE_DIRECTORY} && pwd && docker build -t ${IMAGE_NAME} ."""
                                    )
                                ]
                            )
                        ]
                    )
                }
            }
        }

        // docker compose 이용한 배포
        stage("CD : Deploy") {
            steps {
                script {
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: "${REMOTE_NAME}",
                                verbose: true,
                                transfers: [
                                    sshTransfer(
                                        execCommand: """cd ~${REMOTE_DIRECTORY} && docker compose stop && docker compose up -d --build"""
                                    )
                                ]
                            )
                        ]
                    )
                }
            }
        }
    }
}
