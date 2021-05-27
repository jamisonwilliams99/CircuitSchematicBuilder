# Circuit_simulator

This project allows the user to create simple circuit diagrams.

To place a component:
1. click the button of the component that you would like to place
2. click the point on the grid that you would like to place the component

To connect components with wires:
1. click the wire button (the button with the straight line icon)
2. click the start and end points of the wire that you want to place
- after clicking the first point, a wire preview will be redrawn depending on the position of the mouse cursor.
- simply click a second time to place the finalized wire

To Delete a component or wire segment:
1. click the select button (the button with the mouse cursor icon)
2. click on the component or wire segment that you would like to delete
- the component/wire segment will be highlighted in blue once selected
3. press the 'e' key on your keyboard
- this will clear the component/wire segment from the grid

To rotate a component:
1. click the select button (the button with the mouse cursor icon)
2. click on the component that you would like to rotate
- the component/wire segment will be highlighted in blue once selected
3. press the 'r' key on your keyboard

To assign a value to a component:
1. click the select button (the button with the mouse cursor icon)
2. click on the component that you would like to assign a value to
- the component/wire segment will be highlighted in blue once selected
- a window will also appear once a component is selected, this allows you to assign a voltage value to a voltage source
  or a resistance value to a resistor.
  

# Feauture not fully finished yet
Once a complete circuit has been drawn (every component has been connected by wires), the program can detect components that are in series or parallel. 

Simple circuit analysis rules are applied where components that are in parallel will share the same voltage. 

If the voltage across a resistor is known through being in parallel with a source, and it has been assigned a resistance, then Ohm's Law will be applied to calculate the current.


