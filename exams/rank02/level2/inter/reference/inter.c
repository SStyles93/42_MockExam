#include <unistd.h>

int	main(int argc, char **argv)
{
	int		in_second[256];
	int		printed[256];
	int		i;
	unsigned char	c;

	if (argc == 3)
	{
		i = 0;
		while (i < 256)
		{
			in_second[i] = 0;
			printed[i++] = 0;
		}
		i = 0;
		while (argv[2][i])
			in_second[(unsigned char)argv[2][i++]] = 1;
		i = 0;
		while (argv[1][i])
		{
			c = argv[1][i++];
			if (in_second[c] && !printed[c])
			{
				write(1, &c, 1);
				printed[c] = 1;
			}
		}
	}
	write(1, "\n", 1);
	return (0);
}
