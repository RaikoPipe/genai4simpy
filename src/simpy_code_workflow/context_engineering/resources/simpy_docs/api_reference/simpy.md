# \"simpy\"

The \"simpy\" module aggregates SimPy\'s most used components into a
single namespace. This is purely for convenience. You can of course also
access everything (and more!) via their actual submodules.

The following tables list all the available components in this module.

## Environments

  ------------- --------------------------------------------------------------
  \"Environm    Execution environment for an event-based simulation.
  ent\"(\[ini   
  tial_time \]) 

  \"Realtime    Execution environment for an event-based simulation which is
  Environme     synchronized with the real-time (also known as wall-clock
  nt\"(\[init   time).
  ial_time,     
  factor,       
  \...\])       
  ------------- --------------------------------------------------------------

## Events

  ------------- --------------------------------------------------------------
  \"Event\"(e   An event that may happen at some point in time.
  nv)           

  \"Timeout\"   A \"Event\" that gets processed after a *delay* has passed.
  (env,         
  delay\[,      
  value\])      

  \"Process\"   Process an event yielding generator.
  (env,         
  generator)    

  \"AllOf\"(e   A \"Condition\" event that is triggered if all of a list of
  nv, events)   *events* have been successfully triggered.

  \"AnyOf\"(e   A \"Condition\" event that is triggered if any of a list of
  nv, events)   *events* has been successfully triggered.

  \"Interrup    Exception thrown into a process if it is interrupted (see
  t\"(cause)    \"interrupt()\").
  ------------- --------------------------------------------------------------

## Resources

  -------------- --------------------------------------------------------------
  \"Resource     Resource with *capacity* of usage slots that can be requested
  \"(env\[,      by processes.
  capacity\])    

  \"Priority     A \"Resource\" supporting prioritized requests.
  Resource\"     
  (env\[,        
  capacity\])    

  \"Preempti     A \"PriorityResource\" with preemption.
  veResourc      
  e\"(env\[,     
  capacity\])    

  \"Containe     Resource containing up to *capacity* of matter which may
  r\"(env\[,     either be continuous (like water) or discrete (like apples).
  capacity,      
  init\])        

  \"Store\"(e    Resource with *capacity* slots for storing arbitrary objects.
  nv\[,          
  capacity\])    

  \"Priority     Wrap an arbitrary *item* with an order-able *priority*.
  Item\"(pri     
  ority, item)   

  \"Priority     Resource with *capacity* slots for storing objects in priority
  Store\"(en     order.
  v\[,           
  capacity\])    

  \"FilterSt     Resource with *capacity* slots for storing arbitrary objects
  ore\"(env\[,   supporting filtered get requests.
  capacity\])    
  -------------- --------------------------------------------------------------

## Exceptions

  ------------ --------------------------------------------------------------
  \"SimPyExc   Base class for all SimPy specific exceptions.
  eption\"     

  \"Interrup   Exception thrown into a process if it is interrupted (see
  t\"(cause)   \"interrupt()\").
  ------------ --------------------------------------------------------------
