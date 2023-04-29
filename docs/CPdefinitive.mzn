% Define input variables
int: m;             % Number of couriers
int: n;             % Number of items
set of int: LOADS = 1..m;
array[LOADS] of int: l;    % Maximum load for each courier
set of int: SIZES = 1..n;
array[SIZES] of int: s;    % Size of each item
array[1..n+1, 1..n+1] of int: D;    % Distance matrix


% Define decision variables
array[1..m, 1..n] of var 0..n: routes; % routes for each courier

% Objective
var int: max_distance = max([(sum(j in 1..n) (D[routes[i,j], routes[i,j+1]]) ) + (D[n+1, routes[i,1]]) + | i in 1..m]);

% Constraints
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

% Solve
solve minimize max_distance;

% Output solution
output ["Routes:"] ++ [show(routes[i,:]) ++ "\n" | i in 1..m] ++
       ["Total Distance Travelled: \(max_distance)"];
