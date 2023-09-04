This is an automated battle simulator for Honkai: Star Rail.

The goal is to fully implement the game's battle system (hopefully since the source
code of the game is never available), so that we can test team damage in real battle
environment.

The code is in Python3, so we can potentially apply artificial neural network AI
to play the game optimally.

The game is run by a game manager called StarRailOperatingSystem, which works
similarly to an OS. The units are like applications that can have processes and
threads. The system picks them up in a specific order and executes them. There
is also a public memory shared among all units called the blackboard.
Here is a rough description of the process.
* While the game is not over
  * Find the first unit in the queue
  * Start the unit's turn
    * Check if any unit wants to use Ult
    * Ask the unit for an action (Basic ATK, Skill, etc.)
    * Broadcast the message "Unit x is taking action y" (write on the blackboard)
    * Run the action
      * While the action still has more steps (multiple hits from one Skill):
        * Receive a batch of commands from the unit (damage, heal, etc.)
        * Broadcast the message "Unit x is proposing some commands"
        * Execute the commands
          * If any unit needs to run extra commands (usually caused by the broadcasts)
            * Execute the commands (recursive call)
      * If any unit needs to run extra actions (usually caused by the broadcasts)
        * Run the action (recursive call)
    * Check if any unit wants to use Ult (This one won't run for Seele. Somehow her extra turn has higher priority)
    * Check if any unit wants to run an extra turn
    * Check if any unit wants to use Ult
  * Put the unit back to starting position
  * End the unit's turn

To get started, you can run and modify test.py in console to see some battle results.
The results should look like what's in example_outcome.txt.
Then, read rail_operating_system.py and unit.py  and make sure you fully understand
them. Then read some character implementations to get an idea how characters are
coded. Light cones and relics which may change units' behaviour are implemented
using the decorator design pattern.
