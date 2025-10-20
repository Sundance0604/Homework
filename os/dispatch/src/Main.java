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
                System.out.println("Running HRRN...");
                HRRN.runHRRN(procs); // 将进程数据传递给 HRRN
                break;
            case 4:
                System.out.println("Running HPFRR...");
                HPFRR.runHPFRR(procs); // 将进程数据传递给 HPFRR
                break;
            case 5:
                System.out.println("Running all algorithms...");

                System.out.println("\n--- FCFS Results ---");
                FCFS.runFCFS(new ArrayList<>(procs)); // 传递进程数据的副本给 FCFS

                System.out.println("\n--- SJF Results ---");
                SJF.runSJF(new ArrayList<>(procs)); // 传递进程数据的副本给 SJF

                System.out.println("\n--- HRRN Results ---");
                HRRN.runHRRN(new ArrayList<>(procs)); // 传递进程数据的副本给 HRRN

                System.out.println("\n--- HPFRR Results ---");
                HPFRR.runHPFRR(new ArrayList<>(procs)); // 传递进程数据的副本给 HPFRR

                break;
            default:
                System.out.println("Invalid choice. Exiting...");
        }
    }
}
