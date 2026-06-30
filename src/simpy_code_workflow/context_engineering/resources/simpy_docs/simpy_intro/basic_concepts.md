:::: {#basic_concepts}
::: currentmodule
simpy.core
:::
::::

# Basic Concepts

SimPy is a discrete-event simulation library. The behavior of active
components (like vehicles, customers or messages) is modeled with
*processes*. All processes live in an *environment*. They interact with
the environment and with each other via *events*.

Processes are described by simple Python
[generators](http://docs.python.org/3/reference/expressions.html#yieldexpr).
You can call them *process function* or *process method*, depending on
whether it is a normal function or method of a class. During their
lifetime, they create events and `yield` them in order to wait for them
to occur.

When a process yields an event, the process gets *suspended*. SimPy
*resumes* the process, when the event occurs (we say that the event is
*processed*). Multiple processes can wait for the same event. SimPy
resumes them in the same order in which they yielded that event.

An important event type is the `~simpy.events.Timeout`{.interpreted-text
role="class"}. Events of this type occur (are processed) after a certain
amount of (simulated) time has passed. They allow a process to sleep (or
hold its state) for the given time. A
`~simpy.events.Timeout`{.interpreted-text role="class"} and all other
events can be created by calling the appropriate method of the
`Environment`{.interpreted-text role="class"} that the process lives in
(`Environment.timeout()`{.interpreted-text role="meth"} for example).

## Our First Process

Our first example will be a *car* process. The car will alternately
drive and park for a while. When it starts driving (or parking), it will
print the current simulation time.

So let\'s start:

    >>> def car(env):
    ...     while True:
    ...         print('Start parking at %d' % env.now)
    ...         parking_duration = 5
    ...         yield env.timeout(parking_duration)
    ...
    ...         print('Start driving at %d' % env.now)
    ...         trip_duration = 2
    ...         yield env.timeout(trip_duration)

Our *car* process requires a reference to an
`Environment`{.interpreted-text role="class"} (`env`) in order to create
new events. The *car*\'s behavior is described in an infinite loop.
Remember, this function is a generator. Though it will never terminate,
it will pass the control flow back to the simulation once a `yield`
statement is reached. Once the yielded event is processed (\"it
occurs\"), the simulation will resume the function at this statement.

As I said before, our car switches between the states *parking* and
*driving*. It announces its new state by printing a message and the
current simulation time (as returned by the
`Environment.now`{.interpreted-text role="attr"} property). It then
calls the `Environment.timeout()`{.interpreted-text role="meth"} factory
function to create a `~simpy.events.Timeout`{.interpreted-text
role="class"} event. This event describes the point in time the car is
done *parking* (or *driving*, respectively). By yielding the event, it
signals the simulation that it wants to wait for the event to occur.

Now that the behavior of our car has been modeled, lets create an
instance of it and see how it behaves:

    >>> import simpy
    >>> env = simpy.Environment()
    >>> env.process(car(env))
    <Process(car) object at 0x...>
    >>> env.run(until=15)
    Start parking at 0
    Start driving at 5
    Start parking at 7
    Start driving at 12
    Start parking at 14

The first thing we need to do is to create an instance of
`Environment`{.interpreted-text role="class"}. This instance is passed
into our *car* process function. Calling it creates a *process
generator* that needs to be started and added to the environment via
`Environment.process()`{.interpreted-text role="meth"}.

Note, that at this time, none of the code of our process function is
being executed. Its execution is merely scheduled at the current
simulation time.

The `~simpy.events.Process`{.interpreted-text role="class"} returned by
`~Environment.process()`{.interpreted-text role="meth"} can be used for
process interactions (we will cover that in the next section, so we will
ignore it for now).

Finally, we start the simulation by calling
`~Environment.run()`{.interpreted-text role="meth"} and passing an end
time to it.

## What\'s Next?

You should now be familiar with SimPy\'s terminology and basic concepts.
In the `next section <process_interaction>`{.interpreted-text
role="doc"}, we will cover process interaction.
