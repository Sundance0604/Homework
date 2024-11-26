% 定义区间和节点数量
x_min = -5;
x_max = 5;
num_points = 11;

% 生成等距节点和函数值
x_nodes = linspace(x_min, x_max, num_points);
y_nodes = 1 ./ (1 + x_nodes.^2);

% 生成插值区间内的更多点，用于绘制
x_interp = linspace(x_min, x_max, 200);
f_actual = 1 ./ (1 + x_interp.^2);

% Lagrange 插值 (利用多项式插值)
L_poly = polyfit(x_nodes, y_nodes, num_points - 1);
y_lagrange = polyval(L_poly, x_interp);

% 三次样条插值
y_spline = spline(x_nodes, y_nodes, x_interp);

% 绘制结果
figure;
plot(x_interp, f_actual, 'b-', 'LineWidth', 1.5); hold on;
plot(x_interp, y_lagrange, 'r--', 'LineWidth', 1.5);
plot(x_interp, y_spline, 'g-.', 'LineWidth', 1.5);
plot(x_nodes, y_nodes, 'ko', 'MarkerFaceColor', 'k'); % 插值节点
legend('真实函数 f(x)', '10 次插值多项式 L_{10}(x)', '三次样条插值 S(x)', '插值节点');
xlabel('x');
ylabel('f(x)');
title('函数 f(x) 的插值近似');
grid on;