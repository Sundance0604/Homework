import java.util.*;

public class HRRN {
    // 修改为接收进程数据作为参数
 public static Proc waitCount(List<Proc> ready, double currentTime) {
   
    final double EPS = 1e-12;
    double maxR = -Double.MAX_VALUE;
    int pos = 0;

    for (int i = 0; i < ready.size(); i++) {
        Proc p = ready.get(i);
        double run = Math.max(p.run, EPS);                  // 1) 除零保护
        double wait = Math.max(0.0, currentTime - p.submit); // 2) 等待非负
        double R = 1.0 + wait / run;

        if (R > maxR) {
            maxR = R;
            pos = i;
        } else if (Math.abs(R - maxR) < EPS) {
            // 3) 并列规则（可选）：先到者优先 → 再比运行更短 → 再比ID更小
            Proc best = ready.get(pos);
            if (p.submit < best.submit - EPS ||
               (Math.abs(p.submit - best.submit) < EPS && p.run < best.run - EPS) ||
               (Math.abs(p.submit - best.submit) < EPS && Math.abs(p.run - best.run) < EPS && p.id < best.id)) {
                pos = i;
            }
        }
    }
    return ready.remove(pos);
}

    public static void runHRRN(List<Proc> procs) {
        // HRRN：按提交时间排序
        procs.sort(Comparator.comparingDouble(p -> p.submit));

        List<Proc> scheduled = new ArrayList<>();
        List<Proc> ready = new ArrayList<>(); // 按运行时间排序

        int i = 0;
        int time = 0;

        while (i < procs.size() || !ready.isEmpty()) {
            // 将所有已到达的进程放入 ready 队列
            while (i < procs.size() && procs.get(i).submit <= time + 1e-12) {
                ready.add(procs.get(i));
                i++;
            }
            if (ready.isEmpty()) {
                // 如果没有进程已经到达，跳到下一个进程的提交时间
                time = procs.get(i).submit;
                continue;
            }

            // 更新等待时间
            Proc cur = waitCount(ready, time);
            cur.start = Math.max(time, cur.submit);
            TestIO.finalizeFields(cur);
            time = cur.finish;
            scheduled.add(cur); // 将完成的进程加入调度列表
        }

        // 打印结果
        TestIO.printResults(scheduled);
    }
}
