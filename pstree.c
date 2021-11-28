#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>

#ifdef DEBUG
#define dprintf(...) printf(__VA_ARGS__)
#else
#define dprintf(...)
#endif

#define BUF_SIZE 256
#define MAX_PROC 7192
#define MAX_PROC_ID 0x8000

typedef struct Process {
	int pid;
	int ppid;
	int child_len;
	char* name;
	struct Process* children[MAX_PROC];
}process;

int proc_id_list[MAX_PROC];

process* init_proc[MAX_PROC];
process* proc_list[MAX_PROC_ID];

int proc_num;
int init_proc_num;

// proto type
int scan_process();
process* read_process(int pid);
process* create_process(int pid, int ppid, char *name);
void show_process();
void print_tree(process *p, int layer);

int main() {

	proc_num = scan_process();

	dprintf("proc num: %d\n", proc_num);

	if(proc_num < 0) return -1;

	init_proc_num = 0;

	for(int i = 0; i < proc_num; ++i) {

		dprintf("pid: %d\n", proc_id_list[i]);

		process *p = read_process(proc_id_list[i]);

		if(p == NULL) continue;

		proc_list[p->pid] = p;

		if(p->ppid == 0)
			init_proc[init_proc_num++] = p;

		else
		{
			process *parent = proc_list[p->ppid];
			parent->children[parent->child_len++] = p;
		}

	}

	show_process();

	return 0;
}

process* read_process(int pid) {

	char buf[BUF_SIZE];

	char pid_path[32];

	sprintf(pid_path, "/proc/%d/stat", pid);

	int fd = open(pid_path, O_RDONLY);
	if (fd < 0) return NULL;

	int res = read(fd, buf, BUF_SIZE);
	if (res < 0) return NULL;

	int _pid, ppid;
	char state[4];
	char *name = malloc(sizeof(char)*32);

	sscanf(buf, "%d %s %c %d", &_pid, name, state, &ppid);

	process *p = create_process(pid, ppid, name);

	close(fd);

	return p;
}

process* create_process(int pid, int ppid, char* name) {
	process *p = malloc(sizeof(process));
	p->pid = pid;
	p->name = name;
	p->ppid = ppid;

	p->child_len = 0;
	return p;
}

int scan_process() {

	proc_num = 0;
	struct dirent *dp;

	DIR *dirp = opendir("/proc");
	if(dirp == NULL) return -1;

	for(;;) {
		dp = readdir(dirp);
		if(dp == NULL) break;

		int num = atoi(dp->d_name);
		if(num != 0)
			proc_id_list[proc_num++] = num;

	}

	closedir(dirp);

	return proc_num;
}

void show_process() {

	for(int i = 0; i < init_proc_num; ++i)
		print_tree(init_proc[i], 0);

}

void print_tree(process *p, int layer) {
	for(int i = 0; i < layer; ++i) printf("   ");
	printf("[%d]%s\n", p->pid, p->name);

	layer++;

	for(int j = 0; j < p->child_len; ++j)
		print_tree(p->children[j], layer);
}
