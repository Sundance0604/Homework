
x = [27.7, 28, 29, 30];
y = [4.1, 4.3, 4.1, 3.0];
n = length(x);


S1_prime = 3.0;  % S'(27.7)
S4_prime = -4.0; % S'(30)


h = diff(x);


A = zeros(n);
b = zeros(n, 1);


A(1, 1) = 2 * h(1);       
A(1, 2) = h(1);
b(1) = 6 * ((y(2) - y(1)) / h(1) - S1_prime);

A(n, n-1) = h(n-1);       
A(n, n) = 2 * h(n-1);
b(n) = 6 * (S4_prime - (y(n) - y(n-1)) / h(n-1));


for i = 2:n-1
    A(i, i-1) = h(i-1);
    A(i, i) = 2 * (h(i-1) + h(i));
    A(i, i+1) = h(i);
    b(i) = 6 * ((y(i+1) - y(i)) / h(i) - (y(i) - y(i-1)) / h(i-1));
end


M = A \ b;


coeffs = zeros(n-1, 4);

for i = 1:n-1
    coeffs(i, 1) = y(i);                    % a_i
    coeffs(i, 2) = (y(i+1) - y(i)) / h(i) - (h(i) / 6) * (2 * M(i) + M(i+1)); % b_i
    coeffs(i, 3) = M(i) / 2;                % c_i
    coeffs(i, 4) = (M(i+1) - M(i)) / (6 * h(i)); % d_i
end


disp('每个间隔点的三次样条插值 :');
for i = 1:n-1
    fprintf('间隔点 [%g, %g]: a = %.4f, b = %.4f, c = %.4f, d = %.4f\n', ...
        x(i), x(i+1), coeffs(i, 1), coeffs(i, 2), coeffs(i, 3), coeffs(i, 4));
end
