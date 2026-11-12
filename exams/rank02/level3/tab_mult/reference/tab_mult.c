#include <unistd.h>

static void	put_nbr(long n)
{
	char	c;

	if (n < 0)
	{
		write(1, "-", 1);
		n = -n;
	}
	if (n >= 10)
		put_nbr(n / 10);
	c = '0' + n % 10;
	write(1, &c, 1);
}

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

int	main(int argc, char **argv)
{
	int	n;
	int	i;

	if (argc != 2)
	{
		write(1, "\n", 1);
		return (0);
	}
	n = mini_atoi(argv[1]);
	i = 1;
	while (i <= 9)
	{
		put_nbr(i);
		write(1, " x ", 3);
		put_nbr(n);
		write(1, " = ", 3);
		put_nbr((long)i * n);
		write(1, "\n", 1);
		i++;
	}
	return (0);
}
