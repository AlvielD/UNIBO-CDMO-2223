% INPUT VARIABLES
int: m;                          % Number of couriers
int: n;                          % Number of items
set of int: LOADS = 1..m;
array[LOADS] of int: l;          % Maximum load for each courier
set of int: SIZES = 1..n;
array[SIZES] of int: s;          % Size of each item
array[1..n+1, 1..n+1] of int: D; % Distance matrix


% DECISION VARIABLES
array[1..m, 1..n] of var 0..n: routes; % Routes for each courier

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

% ---------------------------------------------------------------------------------------------------------------------
% OBJECTIVE FUNCTION

% Array containing the distances of the first courier to each distribution point (DOES NOT WORK - Problems with indexes)
% It does NOT contain the distance from Origin to first point.
array[1..n+1] of var opt int: dist_courier = [D[routes[1, j], routes[1, j+1]] | j in 1..n where routes[1, j+1] != 0];

% This was a trial of an array with the total distance of each courier
%array[1..m] of int: dist_courier = [sum(i in i..m)([routes[i, j] | j in 1..n])];

% THIS REMAINED UNCHANGED FROM LAST MEETING
%var int: max_distance = max([(sum(j in 1..n)(D[routes[i,j], routes[i,j+1]]) ) + (D[n+1, routes[i,1]]) + | i in 1..m]);

% ---------------------------------------------------------------------------------------------------------------------

% Solve
solve minimize sum(i in 1..n+1)(dist_courier[i]);

% Output solution
/*output ["Routes:"] ++ [show(routes[i,:]) ++ "\n" | i in 1..m] ++
       ["Total Distance Travelled: \(max_distance)"];*/
       
output ["Objective function value: \(dist_courier)\n"];
