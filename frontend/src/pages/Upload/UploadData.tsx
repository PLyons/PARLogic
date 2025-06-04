import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { uploadFile } from '../../services/api';

interface FileStatus {
  name: string;
  status: 'pending' | 'success' | 'error';
  message?: string;
}

const UploadData: React.FC = () => {
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    const newFiles: FileStatus[] = [];

    for (const file of acceptedFiles) {
      if (!file.name.endsWith('.csv')) {
        newFiles.push({
          name: file.name,
          status: 'error',
          message: 'Only CSV files are allowed',
        });
        continue;
      }

      try {
        const response = await uploadFile(file);
        newFiles.push({
          name: file.name,
          status: 'success',
          message: `${response.message} (${response.rows} rows processed)`,
        });
      } catch (error) {
        newFiles.push({
          name: file.name,
          status: 'error',
          message: error instanceof Error ? error.message : 'Upload failed',
        });
      }
    }

    setFiles((prev) => [...prev, ...newFiles]);
    setUploading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: true,
  });

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Data
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your CSV files containing inventory usage data
      </Typography>

      <Card
        {...getRootProps()}
        sx={{
          mt: 2,
          p: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <UploadIcon color="primary" sx={{ fontSize: 48 }} />
          <Typography variant="h6" align="center">
            {isDragActive
              ? 'Drop the files here'
              : 'Drag and drop files here, or click to select files'}
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            Only CSV files are accepted
          </Typography>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={(e) => e.stopPropagation()}
          >
            Select Files
          </Button>
        </Box>
      </Card>

      {uploading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {files.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload Status
            </Typography>
            <List>
              {files.map((file, index) => (
                <ListItem key={`${file.name}-${index}`}>
                  <ListItemIcon>
                    {file.status === 'success' ? (
                      <CheckIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={file.message}
                    primaryTypographyProps={{
                      color: file.status === 'error' ? 'error' : 'inherit',
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {files.some((file) => file.status === 'error') && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Some files failed to upload. Please check the errors and try again.
        </Alert>
      )}
    </Box>
  );
};

export default UploadData; 