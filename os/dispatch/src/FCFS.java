import java.util.*;

public class FCFS {
    // 修改为接收进程数据作为参数
    public static void runFCFS(List<Proc> procs) {
        // FCFS：按提交时间排序
        procs.sort(Comparator.comparingDouble(p -> p.submit));

        double time = 0.0;
        // 计算每个进程的开始时间、结束时间等
        for (Proc p : procs) {
            p.start = Math.max(time, p.submit);
            TestIO.finalizeFields(p); // 计算结束时间、等待时间、周转时间
            time = p.finish; // 更新时间，作为下一个进程的开始时间
        }

        // 打印结果
        TestIO.printResults(procs);
    }
}
