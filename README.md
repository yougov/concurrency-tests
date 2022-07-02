# concurrency-tests
Concurrency tests with different stacks.

It's basically a comparison between running different stacks for gathering data
from an external service in a concurrent fashion.

Currently, the comparison is between:
1. uWSGI + gevent + Flask
2. Uvicorn + uvloop + FastAPI

There might be more stacks added in the future (like Rocket and NodeJS) just
for experimentation purposes.

# Rationale

The idea is: there's an external service that provides data, so how well does
each stack perform when doing a number of concurrent fetches of data from it?

To simulate this external service I run an Nginx image serving static JSON files
(which were previously randomly generated and are versioned under `fixtures/`),
and then we're able to make requests to Nginx to fetch the JSON data. Nginx is
very fast and consistent, so this allows us to focus more on variations between
application stacks fetching data from it, although still providing 
decently-sized JSON content.

# Dependencies

In order to use this repo you need to have available docker-compose.

# How to test it
1. `$ make up`
2. `$ ./scripts/check-performance.py`

Take a look at the logs from docker-compose, and at the outputs from the script.

What the script does is to run a certain amount of requests for JSON data, which
is consistent between each stack being checked, thus exercising them under very
similar conditions.

# Findings

Spoiler alert: here are some results I get when running on my computer:

```
 $ ./scripts/check-performance.py 
Checking http://localhost:8101/data
[0.08104367200212437, 0.09249140500105568, 0.07991218000097433]
Checking http://localhost:8102/data
[0.876144165002188, 0.8645361960006994, 0.8990603880010894]
```

The first results are from requests done to the uWSGI stack, and the second
results are from requests done to the FastAPI stack.

Now here are the timings I get from inside each handler function when gathering
data from the "external service" (Nginx):

```
concurrency-tests-uwsgi-1               | Took 0.05811190605163574 seconds to gather data
concurrency-tests-uwsgi-1               | Took 0.06990480422973633 seconds to gather data
concurrency-tests-uwsgi-1               | Took 0.05684971809387207 seconds to gather data
concurrency-tests-fastapi-1             | Took 0.6699528694152832 seconds to gather data
concurrency-tests-fastapi-1             | Took 0.6578493118286133 seconds to gather data
concurrency-tests-fastapi-1             | Took 0.6970744132995605 seconds to gather data
```

This is also relevant because it exposes the fact that the way each stack is
able to fetch the data from the external service plays a big role in the
performance to respond with said data to a client.

However, subtracting the time for gathering the data from the response times, we
end up with these timings for the stack to handle the request and then respond:
* uWSGI:
- 0.022931765950488625
- 0.022586600771319354
- 0.02306246190710226
* FastAPI:
- 0.20619129558690474
- 0.20668688417208614
- 0.2019859747015289

So, overall, uWSGI + gevent + Flask ends up being about 9x faster than a similar
Uvicorn + uvloop + FastAPI stack.
