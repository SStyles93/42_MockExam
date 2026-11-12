/* Test harness: every read() returns a random, smaller number of bytes than
 * requested, like the custom read() used by the real exam. Linux only. */
#ifdef __linux__
# include <unistd.h>
# include <sys/syscall.h>

ssize_t	read(int fd, void *buf, size_t count)
{
	static unsigned int	seed = 42;
	size_t				n;

	seed = seed * 1103515245 + 12345;
	n = count;
	if (count > 1)
		n = (seed >> 16) % count + 1;
	return (syscall(SYS_read, fd, buf, n));
}
#else

typedef int	t_mockexam_empty_unit;
#endif
