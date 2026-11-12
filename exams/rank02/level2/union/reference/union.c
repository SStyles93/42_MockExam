#include <unistd.h>

int	main(int argc, char **argv)
{
	int		printed[256];
	int		i;
	int		arg;
	unsigned char	c;

	if (argc == 3)
	{
		i = 0;
		while (i < 256)
			printed[i++] = 0;
		arg = 1;
		while (arg <= 2)
		{
			i = 0;
			while (argv[arg][i])
			{
				c = argv[arg][i++];
				if (!printed[c])
				{
					write(1, &c, 1);
					printed[c] = 1;
				}
			}
			arg++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
