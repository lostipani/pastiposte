# A producer-consumer service for multi-sources data
```mermaid
flowchart LR
  subgraph Extracting
  listHTTP@{ shape: rect, label: "Listener HTTP" } --> s1@{ shape: lean-r, label: "source HTTP" }
  listWS@{ shape: rect, label: "Listener WS" } --> s2@{ shape: lean-r, label: "source WS" }
  end

  listHTTP & listWS --> exc@{ shape: hex, label: "Exchange" }
  exc --> q1@{ shape: das, label: "queue key1" }
  exc --> q2@{ shape: das, label: "queue key2" }

  subgraph Consuming
  q1 & q2 --> Consumer
  end

  Consumer --> db@{ shape: cyl, label: "DB"}

  subgraph Storing
  db
  end
```


## How to run
* Real-world sources:
```
docker compose --project-directory deploy --profile real-world up --build
```
* Simulate sources for offline testing:
```
docker compose --project-directory deploy --profile simulation up --build
```

## How to develop
1. Implement a `broker` from the provided interface.
2. Implement a `consumer` from the provided interface and define its docker
   image configuration.
3. Define the deployment via `docker-compose`.

## Repository tree
```
.
├── build
│   └── a given service
│       ├── Dockerfile
│       └── requirements.txt
|
├── deploy
│   └── docker-compose.yml
|
└── src
    ├── analyst: an example of complex consumer
    │
    ├── commons: definitions shared by more than one service
    │
    ├── interfaces: definitions of services to be made concrete
    │
    ├── queue_logger: an example of simple consumer
    │
    └── server: for simulations
```


## Interfaces
### Listener
```mermaid
classDiagram
    class Listener
    <<interface>> Listener
    Listener <|.. ListenerWS
    Listener <|.. ListenerHTTP
    Listener: +factory(url)
    class ListenerWS{
        +run()
    }
    class ListenerHTTP{
        +run()
    }
```

### Broker
```mermaid
classDiagram
    class Broker
    <<interface>> Broker
    Broker <|.. BrokerList
    Broker <|.. BrokerQueue
    Broker <|.. BrokerRabbitMQ
    Broker: +factory(backend)
    class BrokerList{
        +add(message)
        +get()
        +is_empty()
    }
    class BrokerQueue{
        +add(message)
        +get()
        +is_empty()
    }
    class BrokerRabbitMQ{
        +add(message)
        +get()
        +is_empty()
    }
```

### Consumer
```mermaid
classDiagram
    class Consumer
    <<interface>> Consumer
    Consumer <|.. rabbitMQConsumer
    class rabbitMQConsumer{
        +consume()
    }
```