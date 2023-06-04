include "globals.mzn";
include "alldifferent_except.mzn";
include "count_leq.mzn";
include "count.mzn";
include "value_precede.mzn";


% INPUT VARIABLES
int: m;                          % Number of couriers
int: n;                          % Number of items
set of int: LOADS = 1..m;
array[LOADS] of int: l;          % Maximum load for each courier
set of int: SIZES = 1..n;
array[SIZES] of int: s;          % Size of each item
array[1..n+1, 1..n+1] of int: D; % Distance matrix


% DECISION VARIABLES
array[1..m, 1..n+1] of var 1..n+1: routes; % Routes for each courier


% ---------------------------------------------------------------------------------------------------------------------
% CONSTRAINTS

%All the values of the routes need to be different to each other except for the value n+1
constraint alldifferent_except(routes,{n+1});


%All the values from 1..n needs appear exactly one time in the routes matrix
constraint 
  forall(i in 1..n)(
    count(routes,i,1)
);


% The courier must finished on the origin point 
constraint forall(i in 1..m, j in n-m+2..n+1) (
  routes[i, j] = n + 1
);

%constraint to force to have exactly (m*(n+1))-n n+1s
constraint 
    count(routes,n+1,(m*(n+1))-n);
    

% constraint to force that the total size of items assigned to each courier cannot exceed their maximum load size and constraint to force that the total size of items assigned to each courier is at least the load of the min value of item sizes

constraint
  forall(i in 1..m)(
    sum(j in 1..n where routes[i,j] != n+1)(s[routes[i,j]]) <= l[i] /\ sum(j in 1..n where routes[i,j] != n+1)(s[routes[i,j]]) >= min(s) 
);


% POSSIBLE SIMMETRY BREAKING
% Constraint to force the first value of each row of the matrix to be different from n+1
constraint 
  forall(i in 1..m)(
    routes[i, 1] != n+1
  );


% Force all the numbers after the first n+1 to be also n+1
constraint 
  forall(i in 1..m, j in 1..n)(
      if routes[i,j]==n+1 then routes[i,j+1] = n+1 else true endif
  );


% Constraint to encourage early assignment of items to couriers with available load
constraint forall(i in 1..m, j in 1..n) (
  routes[i, j] == n+1 -> routes[i, j+1] = n+1 \/ sum(k in 1..n where k < j)(routes[i, k] = n+1) > 0
);


% ---------------------------------------------------------------------------------------------------------------------
% OBJECTIVE FUNCTION


%Application of the same objective function above to all couriers 
array[1..m] of var opt int: dist_courier =[sum(j in 1..n)(D[ routes[i, j], routes[i, j+1]]) +(D[n+1, routes[i,1]])|i in 1..m];


% ---------------------------------------------------------------------------------------------------------------------

% Solve
% Search annotations


ann: search_ann1 = int_search(routes, input_order, indomain_min);
ann: search_ann2 = int_search(routes, input_order, indomain_random);
ann: search_ann3 = int_search(routes, first_fail, indomain_min);
ann: search_ann4 = int_search(routes, first_fail, indomain_random);
ann: search_ann5 = int_search(routes, dom_w_deg, indomain_min); 
ann: search_ann6 = int_search(routes, dom_w_deg, indomain_random); 
 


solve :: search_ann6  minimize max(dist_courier);


       
output ["Objective function value: \(dist_courier)\n"];
output ["Routes value: \(routes)\n"];
