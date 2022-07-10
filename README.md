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

## Edit 6: FastAPI + Hypercorn

Just to check if the performance issue could be with Uvicorn, I also added
Hypercorn to the mix. For the results below:

* http://localhost:8101/data is uWSGI + Flask + gevent
* http://localhost:8102/data is uvloop + FastAPI + Uvicorn
* http://localhost:8103/data is uvloop + aiohttp
* http://localhost:8104/data is uvloop + FastAPI + Hypercorn

Here are the results:

```
 $ make check-performance 
python3 scripts/check-performance.py
*** Checking correctness of data ***
Checking http://localhost:8101/data
http://localhost:8101/data is correct
Checking http://localhost:8102/data
http://localhost:8102/data is correct
Checking http://localhost:8103/data
http://localhost:8103/data is correct
Checking http://localhost:8104/data
http://localhost:8104/data is correct
*** Checking performance ***
Checking http://localhost:8101/data
Average: 0.5557943843353618
Timings: [0.5642758260073606, 0.5538909169990802, 0.5492164099996444]
Checking http://localhost:8102/data
Average: 1.678230069000468
Timings: [1.7020821720070671, 1.6667501029878622, 1.6658579320064746]
Checking http://localhost:8103/data
Average: 0.2670309113357992
Timings: [0.26443595500313677, 0.26453293100348674, 0.27212384800077416]
Checking http://localhost:8104/data
Average: 1.7436538100009784
Timings: [1.7575230410002405, 1.7376779810001608, 1.735760408002534]
```

So Hypercorn performed worse than Uvicorn. And there seems to be something being
done in FastAPI that makes it slower than the other stacks, maybe something that
I could simplify in the test app.

## Edit 7: Running on a VM in a remote server

I ran all that stuff, with the latest changes, on a VM that's running on a
remote server, just to check if there would be any surprises when comparing to
them running on my computer. The VM is listed as having only 1 logical core, and
it has 4GB of RAM in total. The tests were run without barely anything else
running, with the same codebase state as the previous test:

```
 $ make check-performance
python3 scripts/check-performance.py
*** Checking correctness of data ***
Checking http://localhost:8101/data
http://localhost:8101/data is correct
Checking http://localhost:8102/data
http://localhost:8102/data is correct
Checking http://localhost:8103/data
http://localhost:8103/data is correct
Checking http://localhost:8104/data
http://localhost:8104/data is correct
*** Checking performance ***
Checking http://localhost:8101/data
Average: 0.613248768573006
Timings: [0.6303591337054968, 0.6183538045734167, 0.5910333674401045]
Checking http://localhost:8102/data
Average: 1.4408962487553556
Timings: [1.454364343546331, 1.4309169836342335, 1.4374074190855026]
Checking http://localhost:8103/data
Average: 0.2993548788751165
Timings: [0.2810085276141763, 0.2922225706279278, 0.32483353838324547]
Checking http://localhost:8104/data
Average: 1.4772176807746291
Timings: [1.490590337663889, 1.4459769548848271, 1.4950857497751713]
```

In that VM FastAPI did run a bit faster than on my computer, and uWSGI and
aiohttp ran a bit slower, but there's still a significant difference in
performance between FastAPI and the other options. uWSGI is at least twice as
fast, and aiohttp is even faster.

## Edit 8: Adding Sanic

Just to test yet another asyncio-based framework, I added Sanic to the mix.

Here are the results, with port 8105 being Sanic served directly and 8106 served
behind Uvicorn:

```
*** Checking performance ***
Checking http://localhost:8101/data
Average: 0.5595273966667568
Timings: [0.595685119999871, 0.5261793409999882, 0.556717729000411]
Checking http://localhost:8102/data
Average: 1.7249857080000766
Timings: [1.763092103999952, 1.712813942000139, 1.6990510780001387]
Checking http://localhost:8103/data
Average: 0.24711097800006124
Timings: [0.2507987750000211, 0.25464237300002424, 0.23589178600013838]
Checking http://localhost:8104/data
Average: 1.7103904253334197
Timings: [1.7158350830000018, 1.7082126370000879, 1.7071235560001696]
Checking http://localhost:8105/data
Average: 0.25828098299992536
Timings: [0.2605192519999946, 0.2685947129998567, 0.24572898399992482]
Checking http://localhost:8106/data
Average: 0.2449119503333653
Timings: [0.24571987999979683, 0.24528555300003063, 0.2437304180002684]
```

So here we have a very interesting situation: Sanic is the fastest of them all,
and even a tiny bit faster when running behind Uvicorn. Which makes me conclude
that it's not Uvicorn which makes FastAPI so slow to respond in our scenario
here.

## Edit 9: Pure Starlette

I've just tested pure Starlette. Here are the results for it running behind
Uvicorn:

```
Checking http://localhost:8107/data
Average: 0.24250185233358934
Timings: [0.2636999240003206, 0.23142165999979625, 0.23238397300065117]
```

So indeed there's something extra being done by FastAPI that makes responses
much slower - because it's based on Starlette, which when running pure has
much better performance.

## Edit 10: Returning raw Response instance

As I suspected, the performance problem in FastAPI lies in the way it handles
the data being returned in the response. It does a fair amount of inspection of
the values, probably to get the OpenAPI stuff right, and this imposes a
considerable performance hit.

Here are the same results as before, but this time returning from the request
handler with a bare Response instance, thus manually encoding the response
payload (FastAPI is ports 8102 and 8104 below):

```
python3 scripts/check-performance.py
*** Checking correctness of data ***
Checking http://localhost:8101/data
http://localhost:8101/data is correct
Checking http://localhost:8102/data
http://localhost:8102/data is correct
Checking http://localhost:8103/data
http://localhost:8103/data is correct
Checking http://localhost:8104/data
http://localhost:8104/data is correct
Checking http://localhost:8105/data
http://localhost:8105/data is correct
Checking http://localhost:8106/data
http://localhost:8106/data is correct
Checking http://localhost:8107/data
http://localhost:8107/data is correct
*** Checking performance ***
Checking http://localhost:8101/data
Average: 0.5492803453331968
Timings: [0.5468588979993001, 0.5586922540005617, 0.5422898839997288]
Checking http://localhost:8102/data
Average: 0.24980172600013853
Timings: [0.29054267300034553, 0.22729272800006584, 0.23156977700000425]
Checking http://localhost:8103/data
Average: 0.25109697366648714
Timings: [0.25375061399972765, 0.24550750499929563, 0.2540328020004381]
Checking http://localhost:8104/data
Average: 0.2413024363331715
Timings: [0.26002944899937575, 0.2304424169997219, 0.23343544300041685]
Checking http://localhost:8105/data
Average: 0.2484863879999466
Timings: [0.23881834100029664, 0.25914031399952364, 0.24750050900001952]
Checking http://localhost:8106/data
Average: 0.2281213440001011
Timings: [0.23330932399949234, 0.21634259300026315, 0.23471211500054778]
Checking http://localhost:8107/data
Average: 0.2612281996665236
Timings: [0.2642462539997723, 0.2647721109997292, 0.2546662340000694]
```

Now FastAPI compares to the other asyncio-based frameworks!

## Edit 11: aiohttp under Gunicorn and under uWSGI

Just for the sake of science (not really, but...), I also added two new takes on
aiohttp: one running under Gunicorn (port 8108 below) and one running under
uWSGI (port 8109 below).

```
Checking http://localhost:8101/data
Average: 0.5857285166663738
Timings: [0.6075965429918142, 0.5707378310034983, 0.5788511760038091]
Checking http://localhost:8102/data
Average: 0.2693211586689965
Timings: [0.26962231600191444, 0.2656774749921169, 0.272663685012958]
Checking http://localhost:8103/data
Average: 0.27253545600008994
Timings: [0.27471838300698437, 0.270809723995626, 0.2720782609976595]
Checking http://localhost:8104/data
Average: 0.2662247866683174
Timings: [0.2537858319992665, 0.27199866699811537, 0.2728898610075703]
Checking http://localhost:8105/data
Average: 0.2634680923365522
Timings: [0.2701641309977276, 0.2661690460081445, 0.2540711000037845]
Checking http://localhost:8106/data
Average: 0.2536975643306505
Timings: [0.26195553899742663, 0.24524874400231056, 0.2538884099922143]
Checking http://localhost:8107/data
Average: 0.24046570600088066
Timings: [0.22387974899902474, 0.2442926579969935, 0.2532247110066237]
Checking http://localhost:8108/data
Average: 0.29463179100033204
Timings: [0.33611946800374426, 0.26753793899843004, 0.2802379659988219]
Checking http://localhost:8109/data
Average: 0.29934803033150575
Timings: [0.30769793200306594, 0.2901989489910193, 0.3001472100004321]
```

Both Gunicorn and uWSGI add a bit of latency to aiohttp, but the benefit is
being able to run multiple processes for the app.
