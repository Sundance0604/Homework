% Given data points
x = 0:0.1:0.4;
y = [1.00000, 0.99500, 0.98007, 0.95534, 0.92106];

% Step size
h = 0.1;

% Calculate forward differences
n = length(y);
diff_table = zeros(n, n);
diff_table(:, 1) = y';

for j = 2:n
    for i = 1:(n - j + 1)
        diff_table(i, j) = diff_table(i + 1, j - 1) - diff_table(i, j - 1);
    end
end

% Coefficients from the first row of the difference table
delta_f = diff_table(1, :);

% Given interpolation point
x_interp = 0.048;
t = (x_interp - x(1)) / h;

% Newton forward interpolation formula for N4(x)
N4 = delta_f(1);
t_term = 1;
for i = 1:4
    t_term = t_term * (t - (i - 1));
    N4 = N4 + (delta_f(i + 1) * t_term) / factorial(i);
end

% Display the interpolated result
fprintf('N4(%.3f) = %.5f\n', x_interp, N4);

% Estimate the maximum error bound
M5 = 1; % Assuming maximum value of the 5th derivative of cos(x) is less than or equal to 1
error_bound = abs(t * (t - 1) * (t - 2) * (t - 3) * (t - 4) * h^5 * M5 / factorial(5));
fprintf('Error bound: %.8e\n', error_bound);
