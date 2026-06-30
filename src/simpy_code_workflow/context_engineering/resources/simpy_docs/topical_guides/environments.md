# Environments

::: currentmodule
simpy.core
:::

A simulation environment manages the simulation time as well as the
scheduling and processing of events. It also provides means to step
through or execute the simulation.

Normal simulations use `~simpy.core.Environment`{.interpreted-text
role="class"}. For real-time simulations, SimPy provides a
`~simpy.rt.RealtimeEnvironment`{.interpreted-text role="class"} (more on
that in `real-time-simulations`{.interpreted-text role="doc"}).

## Simulation control

SimPy is very flexible in terms of simulation execution. You can run
your simulation until there are no more events, until a certain
simulation time is reached, or until a certain event is triggered. You
can also step through the simulation event by event. Furthermore, you
can mix these things as you like.

For example, you could run your simulation until an interesting event
occurs. You could then step through the simulation event by event for a
while; and finally run the simulation until there are no more events
left and your processes have all terminated.

The most important method here is `Environment.run()`{.interpreted-text
role="meth"}:

-   If you call it without any argument (`env.run()`), it steps through
    the simulation until there are no more events left.

    :::: warning
    ::: title
    Warning
    :::

    If your processes run forever (`while True: yield env.timeout(1)`),
    this method will never terminate (unless you kill your script by
    e.g., pressing `Ctrl-C`{.interpreted-text role="kbd"}).
    ::::

-   In most cases it is advisable to stop your simulation when it
    reaches a certain simulation time. Therefore, you can pass the
    desired time via the *until* parameter, e.g.: `env.run(until=10)`.

    The simulation will then stop when the internal clock reaches 10 but
    will not process any events scheduled for time 10. This is similar
    to a new environment where the clock is 0 but (obviously) no events
    have yet been processed.

    If you want to integrate your simulation in a GUI and want to draw a
    process bar, you can repeatedly call this function with increasing
    *until* values and update your progress bar after each call:

    ``` python
    for i in range(100):
        env.run(until=i)
        progressbar.update(i)
    ```

-   Instead of passing a number to `run()`, you can also pass any event
    to it. `run()` will then return when the event has been processed.

    Assuming that the current time is 0, `env.run(until=env.timeout(5))`
    is equivalent to `env.run(until=5)`.

    You can also pass other types of events (remember, that a
    `~simpy.events.Process`{.interpreted-text role="class"} is an event,
    too):

        >>> import simpy
        >>>
        >>> def my_proc(env):
        ...     yield env.timeout(1)
        ...     return 'Monty Python’s Flying Circus'
        >>>
        >>> env = simpy.Environment()
        >>> proc = env.process(my_proc(env))
        >>> env.run(until=proc)
        'Monty Python’s Flying Circus'

::: {#simulation-step}
To step through the simulation event by event, the environment offers
`~Environment.peek()`{.interpreted-text role="meth"} and
`~Environment.step()`{.interpreted-text role="meth"}.
:::

`peek()` returns the time of the next scheduled event or *infinity*
(`float('inf')`) if no future events are scheduled.

`step()` processes the next scheduled event. It raises an
`EmptySchedule`{.interpreted-text role="class"} exception if no event is
available.

In a typical use case, you use these methods in a loop like:

``` python
until = 10
while env.peek() < until:
   env.step()
```

## State access

The environment allows you to get the current simulation time via the
`Environment.now`{.interpreted-text role="attr"} property. The
simulation time is a number without unit and is increased via
`~simpy.events.Timeout`{.interpreted-text role="class"} events.

By default, `now` starts at 0, but you can pass an `initial_time` to the
`Environment`{.interpreted-text role="class"} to use something else.

:::: note
::: title
Note
:::

Although the simulation time is technically unit-less, you can pretend
that it is, for example, in seconds and use it like a timestamp returned
by `time.time()`{.interpreted-text role="func"} to calculate a date or
the day of the week.
::::

The property `Environment.active_process`{.interpreted-text role="attr"}
is comparable to `os.getpid()`{.interpreted-text role="func"} and is
either `None` or pointing at the currently active
`~simpy.events.Process`{.interpreted-text role="class"}. A process is
*active* when its process function is being executed. It becomes
*inactive* (or suspended) when it yields an event.

Thus, it only makes sense to access this property from within a process
function or a function that is called by your process function:

    >>> def subfunc(env):
    ...     print(env.active_process)  # will print "p1"
    >>>
    >>> def my_proc(env):
    ...     while True:
    ...         print(env.active_process)  # will print "p1"
    ...         subfunc(env)
    ...         yield env.timeout(1)
    >>>
    >>> env = simpy.Environment()
    >>> p1 = env.process(my_proc(env))
    >>> env.active_process  # None
    >>> env.step()
    <Process(my_proc) object at 0x...>
    <Process(my_proc) object at 0x...>
    >>> env.active_process  # None

An exemplary use case for this is the resource system: If a process
function calls
`~simpy.resources.resource.Resource.request()`{.interpreted-text
role="meth"} to request a resource, the resource determines the
requesting process via `env.active_process`. Take a [look at the
code](https://gitlab.com/team-simpy/simpy/-/blob/master/src/simpy/resources/base.py)
to see how we do this :-).

## Event creation

To create events, you normally have to import
`simpy.events`{.interpreted-text role="mod"}, instantiate the event
class and pass a reference to the environment to it. To reduce the
amount of typing, the `Environment`{.interpreted-text role="class"}
provides some shortcuts for event creation. For example,
`Environment.event()`{.interpreted-text role="meth"} is equivalent to
`simpy.events.Event(env)`.

Other shortcuts are:

-   `Environment.process()`{.interpreted-text role="meth"}
-   `Environment.timeout()`{.interpreted-text role="meth"}
-   `Environment.all_of()`{.interpreted-text role="meth"}
-   `Environment.any_of()`{.interpreted-text role="meth"}

More details on what the events do can be found in the `guide to events
<events>`{.interpreted-text role="doc"}.

## Miscellaneous

Since Python 3.3, a generator function can have a return value:

``` python
def my_proc(env):
    yield env.timeout(1)
    return 42
```

In SimPy, this can be used to provide return values for processes that
can be used by other processes:

``` python
def other_proc(env):
    ret_val = yield env.process(my_proc(env))
    assert ret_val == 42
```
