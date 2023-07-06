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

% TWO COURIERS CANNOT GO TO THE SAME DISTRIBUTION POINT
% Vale of all the variables must be different (except the value representing the origin point.
constraint alldifferent_except(routes,{n+1});

% THE COURIER MUST FINISH IN THE ORIGIN POINT. (Test removing this constraint)
% Force the value n+1 to appear at least once.
% TODO: Why there is j going from n-m+2 until n+1? (If its an improvement to the original model it should go on another file)
constraint forall(i in 1..m, j in n-m+2..n+1) (
  routes[i, j] = n + 1
);

% ALL ITEMS NEED TO BE DELIVERED
% Force values from 1 to n to appear exactly once
constraint 
  forall(i in 1..n)(
    count(routes,i,1)
);

% EACH COURIER NEEDS TO FINISH AT ORIGIN POINT
%TODO: Here we miss the constraint to force the last element to be an n+1, I guess it was removed because of the following constraint.

% TODO: This also seems like an improvement, it should go in another file. Seems like a replacement for the not implemented constraint above
% Force to have exactly (m*(n+1))-n n+1s (Implied constraint?)
constraint 
    count(routes,n+1,(m*(n+1))-n);
    
% ONCE RETURNED TO ORIGIN, A COURIER CANNOT DELIVER MORE
% Force all the numbers after the first n+1 to be also n+1
constraint 
  forall(i in 1..m, j in 1..n)(
      if routes[i,j]==n+1 then routes[i,j+1] = n+1 else true endif
  );

% NO COURIER CAN OVERLOAD ITSELF & EACH COURIER MUST DELIVER AT LEAST ONE ITEM
% Force that the total size of items assigned to each courier cannot exceed their maximum load size.
% Also force the total size of items assigned to each courier to be at least the load of the min value of item sizes. (Implied constraint?)
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


       
output ["Objective function value: \(max(dist_courier))\n"];
output ["Routes value: \(routes)\n"];
