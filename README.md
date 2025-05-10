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

## Components
### Listener
```mermaid
classDiagram
    Listener <|.. ListenerWS
    Listener <|.. ListenerHTTP
    Listener: +factory(backend)
    class ListenerWS{
        +run
    }
    class ListenerHTTP{
        +run
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