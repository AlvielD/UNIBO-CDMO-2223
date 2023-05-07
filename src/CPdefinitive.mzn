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

%All the values of the routes need to be different to each other excpet for the value 8
constraint alldifferent_except(routes,{n+1});

%The value n+1 needs to appear at least 1 time in the each row of the matrix route
constraint 
  forall(i in 1..m)(
    count_leq([routes[i,j]|j in 1..n+1],n+1,1)
);

%All the values from 1..n needs appear exactly one time in the routes matrix
constraint 
  forall(i in 1..n)(
    count(routes,i,1)
);

% The courier must finished on the origin point 
constraint
  forall(i in 1..m)(
    routes[i, n+1] = n+1
);

% constraint to force that the total size of items assigned to each courier cannot exceed their maximum load size
constraint
  forall(i in 1..m)(
    sum(j in 1..n where routes[i,j] != n+1)(s[routes[i,j]]) <= l[i]
);

% POSSIBLE SIMMETRY BREAKING
% Constraint to force the first value of each row of the matrix to be different from n+1
/*
constraint 
  forall(i in 1..m)(
    routes[i, 1] != n+1
  );
*/

% Force all the numbers after the first n+1 to be also n+1
constraint 
  forall(i in 1..m)(
    forall(j in 1..n)(
       if routes[i,j]==n+1 then routes[i,j+1] = n+1 else true endif
    )
  );

%
constraint
  forall(i in 1..m)(
    min([t | t in 1..n+1 where routes[i,t]!= n+1]) = 1
   );
 
 %
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
