import java.util.*;

public class HPFRR {

    // 选出最高优先数的索引（允许优先数为负），同优先数保留先到次序
    private static int pickHighestIndex(List<Proc> ready) {
        if (ready.isEmpty()) throw new IllegalArgumentException("ready is empty");
        int bestIdx = 0;
        int bestPri = ready.get(0).truePriority;
        for (int i = 1; i < ready.size(); i++) {
            int pri = ready.get(i).truePriority;
            if (pri > bestPri) { // 仅比较优先数
                bestPri = pri;
                bestIdx = i;
            }
        }
        return bestIdx;
    }

    public static void runHPFRR(List<Proc> procs) {
        // 按提交时间排序，便于推进时间线
        procs.sort(Comparator.comparingDouble(p -> p.submit));

        // 初始化剩余时间；若你已在外面赋值，这里可省略
        for (Proc p : procs) {
            p.restTime = p.run;
        }

        List<Proc> ready = new ArrayList<>();
        List<Proc> done  = new ArrayList<>();

        int i = 0;
        int time = 0;                     
        final int MIN_PRI = Integer.MIN_VALUE;        

        while (i < procs.size() || !ready.isEmpty()) {

            // 先装入已到达的进程
            while (i < procs.size() && procs.get(i).submit <= time) {
                ready.add(procs.get(i));
                i++;
            }

            if (ready.isEmpty()) {
                // 没有就绪进程：跳到下一到达时刻
                time = procs.get(i).submit;
                continue;
            }

            // 选出最高优先数
            int idx = pickHighestIndex(ready);
            Proc cur = ready.remove(idx);

            // 记录首次开始时间（仅第一次）
            if (cur.start == 0 && time >= cur.submit) {
                cur.start = time; 
            }

            int exec = Math.min(1, cur.restTime); // 执行片长度为1或剩余时间
            time += exec;
            cur.restTime -= exec;

            if (cur.restTime <= 0) {
                
                cur.finish = time;
                cur.turnaround = cur.finish - cur.submit;
                cur.wait = cur.turnaround - cur.run;
                done.add(cur);
                // 完成不降级
            } else {
                cur.truePriority = Math.max(MIN_PRI, cur.truePriority - 1);
                ready.add(cur);
            }
        }

        
        done.sort(Comparator.comparingDouble(p -> p.finish));
        TestIO.printResults(done);
    }
}
