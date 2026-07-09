# F-DARP : Scenarios and Models solved with Cplex

We solve the F-DARP problem with a MILP, and we analyse two different objective functions. 

We study two objectve functions : 
- Maximization of Avvoided Carbon Emissions (MACE)
- Minimization of the Number of Cars (mNC)

### Description of the scenarios
The scenarios naming follows the same rules. Example : D_15_100_od30_op10_md40_mp20_1.json 
D : Type of scenarios 
15 : number of different stops 
100: number of requests 
od30: There are 30 requests with "only driver" role
op10 : There are 10 requests with "only passenger" role 
md40: there are 40 requests with "mainly driver" role
mp20: there are 10 requests with "mainly passenger" role 
1 : Scenario number 1 with such details

### How do I solve one scenario ?
Pre-requisite : you need Cplex installed in your machine. https://www.ibm.com/products/ilog-cplex-optimization-studio
  1) Go to src/run.py
  2) At the bottom of the file, set the time_limit, the objective-type ("MACE" or "mNC"), and give the scenario path.
  3) Chose the level of comments you want with setting the verbose component. 0: No comments, 1: Few comments, 2: complete comments on the execution
  4) Start the execution.

### How do I find the solution files ? 
1) Go to Results/D , and then open the file corresponding to the scenario.
2) The are two different files you can find : a .json file containing complete informations on the solutions + .png files showing the final itineraries.

### How do I generate new scenarios ? 
1) Go to src/data_generator.py
2) Chose the following parameters : number of only drivers, only passengers, mainly drivers and mainly passengers, 
