include "globals.mzn";
include "alldifferent_except.mzn";
include "count_leq.mzn";
include "count.mzn";



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
/*
constraint forall(j in 1..n) (
    sum(i in 1..m) (bool2int(routes[i,j] = j+1)) = 1
); % each distribution point is visited exactly once

constraint forall(i in 1..m) (
    sum(j in 1..n) (S[j] * bool2int(routes[i,j] > 0)) <= L[i]
); % total size of items assigned to each courier cannot exceed their maximum load size

constraint forall(i in 1..m) (
    routes[i,1] = origin /\ routes[i,n] = origin
); % routes for each courier must start and end at the origin point

constraint forall(i in 1..m) (
    sum(j in 1..n) (D[routes[i,j], routes[i,j+1]]) <= max_distance
); % distance travelled by each courier must be less than or equal to the maximum distance travelled by any courier
*/

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

%add constraint to force that the numbers with a value different from n+1 appear at leftmost of the matrix routes


   

% ---------------------------------------------------------------------------------------------------------------------
% OBJECTIVE FUNCTION

% Array containing the distances of the first courier to each distribution point (DOES NOT WORK - Problems with indexes)
% It does NOT contain the distance from Origin to first point.
%array[1..n+1] of var opt int: dist_courier = [D[routes[1, j], routes[1, j+1]] | j in 1..n+1 where routes[1, j+1] != 0 \/ routes[1, j] != 0];

%Appliction of the same objective function above to all couriers 
array[1..m] of var opt int: dist_courier =[sum(j in 1..n)(D[ routes[i, j], routes[i, j+1]]) +(D[n+1, routes[i,1]])|i in 1..m];        
%[sum(j in 1..n+1)([D[routes[i, j], routes[i, j+1]]| i in 1..m];

% This was a trial of an array with the total distance of each courier
%array[1..m] of int: dist_courier = [sum(i in i..m)([routes[i, j] | j in 1..n])];

% THIS REMAINED UNCHANGED FROM LAST MEETING
%var int: max_distance = max([(sum(j in 1..n)(D[routes[i,j], routes[i,j+1]]) ) + (D[n+1, routes[i,1]]) + | i in 1..m]);

% ---------------------------------------------------------------------------------------------------------------------

% Solve
solve :: int_search(routes, input_order, indomain_min)  minimize sum(i in 1..m)(dist_courier[i]);
%solve minimize sum(i in 1..m)(dist_courier[i]);

% Output solution
/*output ["Routes:"] ++ [show(routes[i,:]) ++ "\n" | i in 1..m] ++
       ["Total Distance Travelled: \(max_distance)"];*/
       
output ["Objective function value: \(dist_courier)\n"];
output ["Routes value: \(routes)\n"];
