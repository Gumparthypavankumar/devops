# Metric Types

1. Counter: Used for measurement that only increase (ex: http_request_total)
2. Gauge: Used when measurement can go up / down (ex: CPU usage)
3. Histogram: This type is generally ideal for request duration because it's a metric that needs to be distributed into
   many buckets
    * This is particularly useful for queries such as How many requests took less than 10ms?

## Filter by Labels

* Labels are case-sensitive ex query: <metric_name>{<selectors>}
  Ex:

```shell 
  http_request_total{path="/"}
  
  # multiple labels: 
  http_request_total{method="GET", path="/"}
```

## Regex Matching

Match all metrics following a path label as /item*

```shell
http_request_total{path=~"^/item.*"}
```

Not Regex:

```shell
http_request_total{path!~"^/item.*"}
```

## Why is Prometheus called a Time-Series Database?

Behind the scenes Prometheus records value of a metric with key as timestamp every X scrape interval, although if you
lookup a metric you get a recent value behind the scenes it's a series of data per metric

If you query a metric directly you will get a recent value which is called **Instant Vector**
If you query a metric specifying range you will get a **Range Vector**

```shell

# Instant Vector
http_request_total

# Range Vector
http_request_total[5m]
```

## Prometheus Functions

The functions accept either a ranger vector / instant vector as input. The most used functions are:

1. rate: Computes an avg/second in a range. It is only applicable to Counter metric type, although technically you can
   use it with
   other metric types the results may be undeterministic. In simple terms checks for frequency. Might average out the
   sudden spike unlike irate
2. irate: Computes an avg/sec in a range for last two data points. It is only applicable to Counter metric type,
   although technically you can use it with
   other metric types the results may be undeterministic. In simple terms checks for volatility (a sudden spike)
3. delta: Computes difference between first and last value of time series in a range vector. It is applicable on Gauge
   type metric.

```shell

rate(http_request_total[5m])

irate(http_request_total[5m])

delta(process_cpu_usage[5m])

```

## Aggregation Operators

They take instant vector as an input and produce scalar vector

1. sum (_ instant_vector) -> single aggregate value
2. avg (_ instant_vector) -> single aggregate value
3. max (_ instant_vector) -> single aggregate value
4. min (_ instant_vector) -> single aggregate value

## Grouping by label before Aggregation

```shell

operator by (<label_name>) (instant_vector)

sum by (method) (rate(http_request_total[5m]))
```

## Aggregation Over Time

They take range vector as an input and produce instant vector

1. sum_over_time (_ range_vector) -> Instant Vector
2. avg_over_time (_ range_vector) -> Instant Vector
3. max_over_time (_ range_vector) -> Instant Vector
4. min_over_time (_ range_vector) -> Instant Vector

## Histogram Queries

We use histogram_quantile function that takes percentile and histogram distribution as input to produce a instant
vector. The distribution only accept a quantile label

```shell
# How 95% of requests are performing
histogram_quantile(0.95, sum by (le) (http_request_duration_seconds_bucket{path="/"}))
```

## Averages and Totals
Common question is compute average number of seconds per request

```markdown
Example:

If in 5m we had:

Total Duration = 50s
Total Requests = 100

rate(Total Duration [5m]) = 50 seconds / 300 second = 0.167 seconds/second
rate(Total Requests [5m]) = 100 requests / 300 seconds = 0.333 requests/second

0.167 seconds/second / 0.333 requests/second (second cancels out)

0.167 seconds / 0.333 requests = 0.5 seconds / request

ex:
rate(http_request_duration_seconds_sum{path="/"}[5m]) / rate(http_request_duration_seconds_count{path="/"}[5m])
```

## Label Manipulation
1. label_replace (input_vector, "<new_label>", "<grouping_vector>", "source_label", "regex_pattern"): Create a new label for matching regex
2. label_join (input_vector, "<new_label>", "<separator>", "<first_label>", "<second_label>"): Combine multiple labels

```shell
label_replace(http_request_total, "testing_label", "$1", "path", "(/.*)")
label_join(http_request_total, "testing_label", ":", "job", "instance")
```

## Resource Metrics
Gauge type metrics used to measure utilization of a resource
1. process_cpu_usage
2. process_memory_usage_bytes

## Visualizing Trends
Rate of change of memory usage in past one hour?

rate function is used for counters the equivalent for gauge type metric is **deriv**

```shell
# process_resident_memory_bytes: Amount of memory used by application

deriv(process_resident_memory_bytes[1h])
```

## Advanced Functions
1. topk (k, <input_vector>): Take instant vector as input and fetch top k values
2. bottomk (k, <input_vector>): Take instant vector as input and fetch bottom k values
