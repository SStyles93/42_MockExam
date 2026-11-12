#include <unistd.h>

static int	mini_atoi(char *s)
{
	int	sign;
	int	n;

	sign = 1;
	n = 0;
	while (*s == ' ' || (*s >= '\t' && *s <= '\r'))
		s++;
	if (*s == '-' || *s == '+')
		if (*s++ == '-')
			sign = -1;
	while (*s >= '0' && *s <= '9')
		n = n * 10 + (*s++ - '0');
	return (n * sign);
}

static void	put_hex(unsigned int n)
{
	if (n >= 16)
		put_hex(n / 16);
	write(1, &"0123456789abcdef"[n % 16], 1);
}

int	main(int argc, char **argv)
{
	if (argc == 2)
		put_hex(mini_atoi(argv[1]));
	write(1, "\n", 1);
	return (0);
}
