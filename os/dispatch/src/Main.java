import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // 获取进程数量
        System.out.println("Please input the total number of processes:");
        int n = Integer.parseInt(sc.nextLine().trim());

        // 生成进程数据
        List<Proc> procs = TestIO.generateRandomProcesses(n);

        // 用户选择调度算法
        int choice = TestIO.getAlgorithmChoice(sc);

        switch (choice) {
            case 1:
                System.out.println("Running FCFS...");
                FCFS.runFCFS(procs); // 将进程数据传递给 FCFS
                break;
            case 2:
                System.out.println("Running SJF...");
                SJF.runSJF(procs); // 将进程数据传递给 SJF
                break;
            case 3:
                System.out.println("Running both FCFS and SJF...");
                System.out.println("Running FCFS...");
                FCFS.runFCFS(procs); // 同一数据执行 FCFS
                System.out.println("Running SJF...");
                SJF.runSJF(procs); // 同一数据执行 SJF
                break;
            default:
                System.out.println("Invalid choice. Exiting...");
        }
    }
}
