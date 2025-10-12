import java.util.*;

public class SJF {
    // 修改为接收进程数据作为参数
    public static void runSJF(List<Proc> procs) {
        // SJF：按提交时间排序
        procs.sort(Comparator.comparingDouble(p -> p.submit));

        List<Proc> scheduled = new ArrayList<>();
        PriorityQueue<Proc> ready = new PriorityQueue<>(Comparator.comparingDouble(p -> p.run)); // 按运行时间排序

        int i = 0;
        double time = 0.0;

        while (i < procs.size() || !ready.isEmpty()) {
            // 将所有已到达的进程放入 ready 队列
            while (i < procs.size() && procs.get(i).submit <= time + 1e-12) {
                ready.offer(procs.get(i));
                i++;
            }

            if (ready.isEmpty()) {
                // 如果没有进程已经到达，跳到下一个进程的提交时间
                time = procs.get(i).submit;
                continue;
            }

            // 选择运行时间最短的进程
            Proc cur = ready.poll();
            cur.start = Math.max(time, cur.submit);
            TestIO.finalizeFields(cur);
            time = cur.finish;
            scheduled.add(cur); // 将完成的进程加入调度列表
        }

        // 打印结果
        TestIO.printResults(scheduled);
    }
}
