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
