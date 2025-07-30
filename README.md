# A producer-consumer service for multi-sources data
```mermaid
flowchart TD
  listHTTP@{ shape: rect, label: "listener HTTP" } --> s1@{ shape: doc, label: "source HTTP" }
  listWS@{ shape: rect, label: "listener WS" } --> s2@{ shape: doc, label: "source WS" }
  listHTTP & listWS --> exc@{ shape: hex, label: "Exchange" }
  exc --> q1@{ shape: subproc, label: "queue key1" } --> analyst
  exc --> q2@{ shape: subproc, label: "queue key2" } --> analyst
```

## How to run
* Real-world sources:
```
docker compose --profile real-world up --build
```
* Simulate sources for offline testing:
```
docker compose --profile simulation up --build
```

## Architecture

### Repository tree
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


## Relevant structures
### Listener
```mermaid
classDiagram
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
