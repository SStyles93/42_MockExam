#include <unistd.h>

int	main(int argc, char **argv)
{
	char	*s;
	int		end;
	int		start;
	int		first;

	if (argc == 2)
	{
		s = argv[1];
		end = 0;
		while (s[end])
			end++;
		first = 1;
		while (end > 0)
		{
			while (end > 0 && (s[end - 1] == ' ' || s[end - 1] == '\t'))
				end--;
			start = end;
			while (start > 0 && s[start - 1] != ' ' && s[start - 1] != '\t')
				start--;
			if (start < end)
			{
				if (!first)
					write(1, " ", 1);
				write(1, s + start, end - start);
				first = 0;
			}
			end = start;
		}
	}
	write(1, "\n", 1);
	return (0);
}
