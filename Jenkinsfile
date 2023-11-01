pipeline {
    agent any
    stages {
        stage('Init') {
            steps {
                echo 'Testing..'
                telegramSend(message: 'Building job: $PROJECT_NAME ... - Link: $BUILD_URL', chatId: -740504133)
            }
        }
        stage ('Deployments') {
            steps {
                echo 'Deploying to Production environment...'
                echo 'Copy project over SSH...'
                sshPublisher(publishers: [
                    sshPublisherDesc(
                        configName: 'swarm1',
                        transfers:
                            [sshTransfer(
                                cleanRemote: false,
                                excludes: '',
                                execCommand: "docker build -t registry.thinklabs.com.vn:5000/tclinicaiapi ./thinklabsdev/tclinicaiapiCI/ \
                                    && docker image push registry.thinklabs.com.vn:5000/tclinicaiapi \
                                    && docker service rm tclinicai_api || true \
                                    && docker stack deploy -c ./thinklabsdev/tclinicaiapiCI/docker-compose.yml tclinicai \
                                    && rm -rf ./thinklabsdev/tclinicaiapiCIB \
                                    && mv ./thinklabsdev/tclinicaiapiCI/ ./thinklabsdev/tclinicaiapiCIB",
                                execTimeout: 1800000,
                                flatten: false,
                                makeEmptyDirs: false,
                                noDefaultExcludes: false,
                                patternSeparator: '[, ]+',
                                remoteDirectory: './thinklabsdev/tclinicaiapiCI',
                                remoteDirectorySDF: false,
                                removePrefix: '',
                                sourceFiles: '*, classify/, data/, models/, segment/, utils/'
                            )],
                        usePromotionTimestamp: false,
                        useWorkspaceInPromotion: false,
                        verbose: false
                    )
                ])
                telegramSend(message: 'Building job: $PROJECT_NAME ... - Link: $BUILD_URL', chatId: -740504133)
            }
        }
    }
}
