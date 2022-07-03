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

# Updates / edits

## Edit 1: AsyncClient as a global variable

After making the AsyncClient a global object started together with the app, I
managed to get better timings from FastAPI because of avoiding the boilerplate
latency for setting up the client pool:

```
 $ ./scripts/check-performance.py 
Checking http://localhost:8101/data
[0.09677495100186206, 0.0804886539990548, 0.08643015100096818]
Checking http://localhost:8102/data
[0.27411253199898056, 0.2451330690018949, 0.2572915169985208]
```

But it's still significantly slower than uWSGI (although noticeably faster than 
the previous FastAPI implementation).

## Edit 2: aiohttp as client

After adding aiohttp and making `aiohttp.ClientSession` a global session I also
got a bit more improvement:

```
 $ ./scripts/check-performance.py 
Checking http://localhost:8101/data
[0.10453539900117903, 0.07663203999982215, 0.08214562500143074]
Checking http://localhost:8102/data
[0.2804249090004305, 0.21994025399908423, 0.2271890380034165]
```

But it's still significantly slower than uWSGI (although a bit faster than 
the previous FastAPI tests).

## Edit 3: Increasing everything

After increasing the size of the files, the number of timeit calls and the
repetitions, I got an even more dramatic difference:

```
 $ ./scripts/check-performance.py 
Checking http://localhost:8101/data
[2.631773353990866, 2.5597720590012614, 2.6319224660110194, 2.5842257650074316]
Checking http://localhost:8102/data
[16.15418745999341, 16.162098834989592, 16.20327517199621, 16.071328858990455]
```

This makes it more pronounced that the delivery of the response payload is the
big difference between those stacks. Still trying to find out why and what's
causing that.

## Edit 4: Optimizing Uvicorn as much as I can

I now made sure I wasn't running barely anything else than the stacks in my
computer, and forced Uvicorn to run with httptools and uvloop (just in case it
wasn't using one or either of them), and here were my results now:

```
 $ ./scripts/check-performance.py 
Checking http://localhost:8101/data
[2.527190361986868, 2.5403314139985014, 2.5657907629938563, 2.5391202510072617]
Checking http://localhost:8102/data
[16.13299038200057, 16.14415543198993, 16.0113767899893, 15.997932392012444]
```

All cases are slightly better than before, for all stacks, but still a huge
performance difference between the stacks.

## Edit 5: Adding aiohttp server

I added aiohttp as a server to the mix, to get a grasp of how it performs,
expecting it to perform similarly to FastAPI + Uvicorn. Much to my surprise, it
not only performed way better than FastAPI + Uvicorn, but also a bit better than
uWSGI + Flask which was my performance reference. For the results below:

* http://localhost:8103/data is aiohttp with normal asyncio loop
* http://localhost:8104/data is aiohttp with uvloop

```
 $ make check-performance 
python3 scripts/check-performance.py
*** Checking performance ***
Checking http://localhost:8101/data
Average: 2.6458381063324246
Timings: [2.6972674790013116, 2.6148150009976234, 2.625431838998338]
Checking http://localhost:8102/data
Average: 16.227512442007235
Timings: [16.273041088003083, 16.196980773005635, 16.212515465012984]
Checking http://localhost:8103/data
Average: 1.9147164596652146
Timings: [1.927170394003042, 1.9134009429981234, 1.9035780419944786]
Checking http://localhost:8104/data
Average: 1.843575427332932
Timings: [1.8504752360022394, 1.8394017569953576, 1.8408492890011985]
*** Checking correctness of data ***
Checking http://localhost:8101/data
http://localhost:8101/data is correct
Checking http://localhost:8102/data
http://localhost:8102/data is correct
Checking http://localhost:8103/data
http://localhost:8103/data is correct
Checking http://localhost:8104/data
http://localhost:8104/data is correct
```

Same stuff as above, but with fewer items in each response payload:

```
 $ make check-performance 
python3 scripts/check-performance.py
*** Checking performance ***
Checking http://localhost:8101/data
Average: 0.5782370129988218
Timings: [0.5935518369951751, 0.5747218600008637, 0.5664373420004267]
Checking http://localhost:8102/data
Average: 1.7061704700026894
Timings: [1.776460016000783, 1.6743788240128197, 1.6676725699944654]
Checking http://localhost:8103/data
Average: 0.3183802133329057
Timings: [0.33034264300658833, 0.3127249029930681, 0.3120730939990608]
Checking http://localhost:8104/data
Average: 0.28490452833163243
Timings: [0.2977750389982248, 0.2825904119963525, 0.27434813400032]
*** Checking correctness of data ***
Checking http://localhost:8101/data
http://localhost:8101/data is correct
Checking http://localhost:8102/data
http://localhost:8102/data is correct
Checking http://localhost:8103/data
http://localhost:8103/data is correct
Checking http://localhost:8104/data
http://localhost:8104/data is correct
```

which gives an even more pronounced performance improvement for aiohttp.
