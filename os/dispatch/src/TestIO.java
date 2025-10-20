import java.util.*;
import java.io.*;

class Proc {
    int id;
    int submit;   // 提交时间
    int run;      // 运行时间
    int start;    // 开始时间
    int finish;   // 结束时间
    int wait;     // 等待时间
    int turnaround; // 周转时间
    int restTime; // 剩余时间（可选）
    int priority; // 优先级（可选）
    int truePriority; // 初始优先级（可选）
    // 构造函数
    Proc(int id, int submit, int run, int priority) {
        this.id = id;
        this.submit = submit;
        this.run = run;
        this.priority = priority;
        this.truePriority = priority;
        this.restTime = run;
    }
}

class TestIO {
    // 生成随机进程
    static List<Proc> generateRandomProcesses(int n) {
        List<Proc> list = new ArrayList<>();
        Random rand = new Random();

        // 生成不重复的优先级
        List<Integer> priorities = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            priorities.add(i);
        }
        Collections.shuffle(priorities);

        // 随机生成提交时间和运行时间
        for (int i = 0; i < n; i++) {
            int submit = 5 + rand.nextInt(6);   // 提交时间 5~10
            int run = 1 + rand.nextInt(10);     // 运行时间 1~10
            int priority = priorities.get(i);   // 优先级唯一
            list.add(new Proc(i + 1, submit, run, priority));
        }

        // ✅ 打印生成的进程信息
        System.out.println("=== Generated Processes ===");
        System.out.printf("%-6s %-8s %-6s %-10s %-10s%n", 
                "ID", "submit", "run", "priority", "restTime");

        for (Proc p : list) {
            System.out.printf("%-6d %-8d %-6d %-10d %-10d%n", 
                    p.id, p.submit, p.run, p.priority, p.restTime);
        }
        System.out.println("===========================\n");

        return list;
    }


    // 打印结果表格，按开始时间升序
    static void printResults(List<Proc> procs) {
        procs.sort(Comparator.comparingInt(p -> p.start)); // 按开始时间排序

        // 打印表头
        System.out.printf("%-6s %-8s %-6s %-10s %-8s %-6s %-11s %-10s%n",
                "ID", "submit", "run", "starting", "final", "wait", "turnaround", "priority");

        double sumTa = 0.0;
        for (Proc p : procs) {
            System.out.printf("%-6d %-8d %-6d %-10d %-8d %-6d %-11d %-10d%n",
                    p.id, p.submit, p.run, p.start, p.finish, p.wait, p.turnaround, p.priority);
            sumTa += p.turnaround;
        }

        double avg = procs.isEmpty() ? 0.0 : sumTa / procs.size();
        System.out.printf("The average turnaround time is %.3f%n", avg);
    }


    // 计算每个进程的结束时间、等待时间、周转时间
    static void finalizeFields(Proc p) {
        p.finish = p.start + p.run;
        p.wait = p.start - p.submit;
        p.turnaround = p.finish - p.submit;
    }
    
    // 获取用户输入的进程数量
    static int getProcessCount(Scanner sc) {
        System.out.println("Please input the total number of processes:");
        return Integer.parseInt(sc.nextLine().trim());
    }

    // 获取用户选择的调度算法
    static int getAlgorithmChoice(Scanner sc) {
        System.out.println("What kind of algorithm do you want?");
        System.out.println("Please input 1 to select FCFS, 2 to select SJF, 3 to select HRRN, 4 to select HPFRR ,5 to all.");
        return Integer.parseInt(sc.nextLine().trim());
    }
}
