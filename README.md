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
---
  config:
    class:
      hideEmptyMembersBox: true
---
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
---
  config:
    class:
      hideEmptyMembersBox: true
---
classDiagram
    Broker <|.. BrokerList
    Broker <|.. BrokerQueue
    Broker <|.. BrokerRabbitMQ
    Broker: +factory(backend)
    class BrokerList{
        +add()
        +get()
        +is_empty()
    }
    class BrokerQueue{
        +add()
        +get()
        +is_empty()
    }
    class BrokerRabbitMQ{
        +add()
        +get()
        +is_empty()
    }
```