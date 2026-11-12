#include <stdio.h>
#include <stdlib.h>

char	*get_next_line(int fd);

int	main(void)
{
	char	*line;
	int		count;

	count = 0;
	line = get_next_line(0);
	while (line)
	{
		printf("[%s]\n", line);
		free(line);
		count++;
		line = get_next_line(0);
	}
	printf("NULL after %d line(s)\n", count);
	line = get_next_line(0);
	printf("next call: %s\n", line ? "not NULL" : "NULL");
	free(line);
	return (0);
}
